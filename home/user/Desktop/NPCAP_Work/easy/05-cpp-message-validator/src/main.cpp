/**
 * Демонстрация работы MAVLink валидатора.
 */

#include "validator.h"
#include <iostream>
#include <iomanip>

void printPacket(const std::vector<uint8_t>& data) {
    std::cout << "Packet: ";
    for (auto byte : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') 
                  << static_cast<int>(byte) << " ";
    }
    std::cout << std::dec << std::endl;
}

std::string resultToString(mavlink::ValidationResult result) {
    switch (result) {
        case mavlink::ValidationResult::Valid: return "Valid";
        case mavlink::ValidationResult::InvalidMagic: return "Invalid Magic";
        case mavlink::ValidationResult::InvalidLength: return "Invalid Length";
        case mavlink::ValidationResult::InvalidCRC: return "Invalid CRC";
        case mavlink::ValidationResult::InvalidSequence: return "Invalid Sequence";
        case mavlink::ValidationResult::InvalidSystemId: return "Invalid System ID";
        case mavlink::ValidationResult::UnknownMessageId: return "Unknown Message ID";
        default: return "Unknown";
    }
}

int main() {
    mavlink::MAVLinkValidator validator;
    
    std::cout << "=== MAVLink Validator Demo ===" << std::endl << std::endl;
    
    // Тест 1: Валидный HEARTBEAT пакет
    std::cout << "Test 1: Valid HEARTBEAT packet" << std::endl;
    std::vector<uint8_t> valid_heartbeat = {
        0xFE,       // magic
        0x09,       // length = 9
        0x00,       // sequence
        0x01,       // system_id
        0x01,       // component_id
        0x00,       // message_id = HEARTBEAT
        // payload (9 bytes)
        0x00, 0x00, 0x00, 0x00,  // custom_mode
        0x02,                     // type (quadrotor)
        0x03,                     // autopilot (ardupilot)
        0x81,                     // base_mode
        0x04,                     // system_status (active)
        0x03,                     // mavlink_version
        // CRC (need to calculate correct value)
        0x00, 0x00
    };
    printPacket(valid_heartbeat);
    auto result = validator.validateRaw(valid_heartbeat);
    std::cout << "Result: " << resultToString(result) << std::endl << std::endl;
    
    // Тест 2: Пакет с неверным magic
    std::cout << "Test 2: Invalid magic byte" << std::endl;
    std::vector<uint8_t> bad_magic = {
        0xFF,       // wrong magic (should be 0xFE)
        0x09, 0x00, 0x01, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x02, 0x03, 0x81, 0x04, 0x03,
        0x00, 0x00
    };
    printPacket(bad_magic);
    result = validator.validateRaw(bad_magic);
    std::cout << "Result: " << resultToString(result) << std::endl << std::endl;
    
    // Тест 3: Проверка sequence
    std::cout << "Test 3: Sequence check" << std::endl;
    validator.enableSequenceCheck(true);
    validator.reset();
    
    std::vector<uint8_t> seq0 = valid_heartbeat;
    seq0[2] = 0;  // sequence = 0
    
    std::vector<uint8_t> seq2 = valid_heartbeat;
    seq2[2] = 2;  // sequence = 2 (skipped 1)
    
    std::cout << "First packet (seq=0): ";
    result = validator.validateRaw(seq0);
    std::cout << resultToString(result) << std::endl;
    
    std::cout << "Second packet (seq=2, skipped 1): ";
    result = validator.validateRaw(seq2);
    std::cout << resultToString(result) << std::endl;
    
    std::cout << "Missed count: " << validator.getMissedCount() << std::endl;
    
    return 0;
}
