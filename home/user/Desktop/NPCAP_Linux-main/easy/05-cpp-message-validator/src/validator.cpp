/**
 * MAVLink Message Validator - реализация валидатора MAVLink сообщений.
 * 
 * Задание: реализуйте методы класса MAVLinkValidator.
 */

#include "validator.h"
#include <cstring>
#include <iostream>

namespace mavlink {

// Вычисление CRC по одному байту
uint16_t crc_accumulate(uint8_t data, uint16_t crc) {
    uint8_t tmp = data ^ (crc & 0xFF);
    tmp ^= (tmp << 4);
    return (crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4);
}

// Таблица CRC extra значений
const std::unordered_map<uint8_t, uint8_t> MAVLinkValidator::crc_extra_table_ = {
    {0, 50},    // HEARTBEAT
    {1, 124},   // SYS_STATUS
    {24, 24},   // GPS_RAW_INT
    {30, 39},   // ATTITUDE
    {33, 104},  // GLOBAL_POSITION_INT
    {74, 20},   // VFR_HUD
    {76, 152},  // COMMAND_LONG
    {77, 143},  // COMMAND_ACK
};

// Константы MAVLink v1
constexpr uint8_t MAVLINK_STX_V1 = 0xFE;
constexpr size_t MAVLINK_HEADER_SIZE = 6;  // magic + len + seq + sys + comp + msg
constexpr size_t MAVLINK_CRC_SIZE = 2;


MAVLinkValidator::MAVLinkValidator()
    : expected_system_id_(0)
    , check_sequence_(false)
    , last_sequence_(0)
    , first_message_(true)
    , missed_count_(0) {
}

void MAVLinkValidator::setExpectedSystemId(uint8_t id) {
    expected_system_id_ = id;
}

void MAVLinkValidator::enableSequenceCheck(bool enable) {
    check_sequence_ = enable;
}

uint8_t MAVLinkValidator::getLastSequence() const {
    return last_sequence_;
}

uint32_t MAVLinkValidator::getMissedCount() const {
    return missed_count_;
}

void MAVLinkValidator::reset() {
    last_sequence_ = 0;
    first_message_ = true;
    missed_count_ = 0;
}

// Получение CRC_EXTRA по словарю
std::optional<uint8_t> MAVLinkValidator::getCrcExtra(uint8_t message_id) const {
    auto it = crc_extra_table_.find(message_id);
    if (it != crc_extra_table_.end()) {
        return it->second;
    }
    return std::nullopt;
}

// Полное вычисление CRC, алгоритм X.25 CRC
uint16_t MAVLinkValidator::calculateCrc(const std::vector<uint8_t>& data, uint8_t crc_extra) const {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc = crc_accumulate(byte, crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    return crc;
}

std::optional<MAVLinkMessage> MAVLinkValidator::parse(const std::vector<uint8_t>& data) {
    // Проверка минимальной длины пакета
    if (data.size() < MAVLINK_HEADER_SIZE + MAVLINK_CRC_SIZE) {
        return std::nullopt;
    }

    // Извлечение magic
    uint8_t magic = data[0];
    if (magic != MAVLINK_STX_V1) {  
        return std::nullopt;
    }
    
    // Извлечение length
    uint8_t length = data[1];
    
    // Проверка достаточности данных
    size_t expected_size = MAVLINK_HEADER_SIZE + length + MAVLINK_CRC_SIZE; 
    if (data.size() != expected_size) {
        return std::nullopt;
    }
    
    // Извлечение остального HEADER
    uint8_t sequence = data[2];
    uint8_t system_id = data[3];
    uint8_t component_id = data[4];
    uint8_t message_id = data[5];
    
    // Извлечение Payload 
    std::vector<uint8_t> payload(data.begin() + MAVLINK_HEADER_SIZE, 
                                   data.begin() + MAVLINK_HEADER_SIZE + length);
    
    // Извлечение CRC
    size_t crc_offset = MAVLINK_HEADER_SIZE + length + MAVLINK_CRC_SIZE;
    uint16_t received_crc = data[crc_offset] | (data[crc_offset + 1] << 8);
    
    // Создание сообщения
    MAVLinkMessage message;
    message.magic = magic;
    message.length = length;
    message.sequence = sequence;
    message.system_id = system_id;
    message.component_id = component_id;
    message.message_id = message_id;
    message.payload = payload;
    message.crc = received_crc;
    
    return message;
}
  
ValidationResult MAVLinkValidator::validate(const MAVLinkMessage& msg) {
    // Проверка STX
    if (msg.magic != MAVLINK_STX_V1) {
        return ValidationResult::InvalidMagic;
    }
    
    // Проверка Message ID
    auto crc_extra_opt = getCrcExtra(msg.message_id);
    if (!crc_extra_opt.has_value()) {
        return ValidationResult::UnknownMessageId;
    }
    uint8_t crc_extra = crc_extra_opt.value();
    
    // Создание вектора байтов для вычисления CRC
    std::vector<uint8_t> crc_data;
    crc_data.push_back(msg.length);
    crc_data.push_back(msg.sequence);
    crc_data.push_back(msg.system_id);
    crc_data.push_back(msg.component_id);
    crc_data.push_back(msg.message_id);
    crc_data.insert(crc_data.end(), msg.payload.begin(), msg.payload.end());
    
    // Вычисление CRC
    uint16_t calculated_crc = calculateCrc(crc_data, crc_extra);
    if (calculated_crc != msg.crc) {
        return ValidationResult::InvalidCRC;
    }
    
    // Проверка System ID
    if (expected_system_id_ != 0 && msg.system_id != expected_system_id_) {
        return ValidationResult::InvalidSystemId;
    }
    
    // Проверка Sequence
    if (check_sequence_) {
        if (!first_message_) {
            uint8_t expected_seq = (last_sequence_ + 1);
            if (msg.sequence != expected_seq) {
                return ValidationResult::InvalidSequence;
            }
        }
        reset();
    }
    
    return ValidationResult::Valid;
}

ValidationResult MAVLinkValidator::validateRaw(const std::vector<uint8_t>& data) {
    auto msg_opt = parse(data);
    if (!msg_opt.has_value()) {
        return ValidationResult::InvalidLength;
    }
    return validate(msg_opt.value());
}

}  // namespace mavlink
