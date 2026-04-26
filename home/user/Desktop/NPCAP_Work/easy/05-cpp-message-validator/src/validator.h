#pragma once

#include <cstdint>
#include <optional>
#include <vector>
#include <unordered_map>

namespace mavlink {

/// Результат валидации MAVLink сообщения.
enum class ValidationResult {
    Valid,              ///< Сообщение валидно
    InvalidMagic,       ///< Неверный стартовый байт
    InvalidLength,      ///< Неверная длина пакета
    InvalidCRC,         ///< Неверная контрольная сумма
    InvalidSequence,    ///< Пропущены сообщения (sequence gap)
    InvalidSystemId,    ///< Неожиданный system_id
    UnknownMessageId    ///< Неизвестный тип сообщения
};

/// Распарсенное MAVLink сообщение.
struct MAVLinkMessage {
    uint8_t magic;          ///< Стартовый байт (0xFE для v1)
    uint8_t length;         ///< Длина payload
    uint8_t sequence;       ///< Sequence number
    uint8_t system_id;      ///< System ID
    uint8_t component_id;   ///< Component ID
    uint8_t message_id;     ///< Message ID
    std::vector<uint8_t> payload;  ///< Данные сообщения
    uint16_t crc;           ///< Контрольная сумма
};

/// Валидатор MAVLink сообщений.
class MAVLinkValidator {
public:
    MAVLinkValidator();
    
    /// Установить ожидаемый system_id.
    /// @param id System ID для фильтрации (0 = принимать все)
    void setExpectedSystemId(uint8_t id);
    
    /// Включить/выключить проверку sequence.
    /// @param enable true для включения проверки
    void enableSequenceCheck(bool enable);
    
    /// Распарсить сырые байты в структуру сообщения.
    /// @param data Сырые байты пакета
    /// @return Сообщение или nullopt если парсинг не удался
    std::optional<MAVLinkMessage> parse(const std::vector<uint8_t>& data);
    
    /// Валидировать распарсенное сообщение.
    /// @param msg Сообщение для валидации
    /// @return Результат валидации
    ValidationResult validate(const MAVLinkMessage& msg);
    
    /// Распарсить и валидировать сырые байты.
    /// @param data Сырые байты пакета
    /// @return Результат валидации
    ValidationResult validateRaw(const std::vector<uint8_t>& data);
    
    /// Получить последний валидный sequence number.
    /// @return Sequence number последнего валидного сообщения
    uint8_t getLastSequence() const;
    
    /// Получить количество пропущенных сообщений.
    /// @return Счётчик пропущенных сообщений
    uint32_t getMissedCount() const;
    
    /// Сбросить состояние валидатора.
    void reset();
    
private:
    uint8_t expected_system_id_;
    bool check_sequence_;
    uint8_t last_sequence_;
    bool first_message_;
    uint32_t missed_count_;
    
    /// Таблица CRC extra значений для известных сообщений.
    static const std::unordered_map<uint8_t, uint8_t> crc_extra_table_;
    
    /// Получить CRC extra для message_id.
    /// @param message_id ID сообщения
    /// @return CRC extra или nullopt если сообщение неизвестно
    std::optional<uint8_t> getCrcExtra(uint8_t message_id) const;
    
    /// Вычислить CRC для данных.
    /// @param data Данные для расчёта CRC
    /// @param crc_extra Дополнительный байт CRC
    /// @return Вычисленная контрольная сумма
    uint16_t calculateCrc(const std::vector<uint8_t>& data, uint8_t crc_extra) const;
};

}  // namespace mavlink
