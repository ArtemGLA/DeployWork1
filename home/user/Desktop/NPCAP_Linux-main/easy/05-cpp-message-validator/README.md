# Задание 5: MAVLink Message Validator

**Уровень:** Лёгкий  
**Технологии:** C++ (без Qt)  
**Время выполнения:** 2-3 часа

## Описание

MAVLink пакеты содержат контрольную сумму (CRC) для проверки целостности данных. При передаче по радиоканалу данные могут повреждаться, поэтому валидация важна.

В этом задании вам нужно написать валидатор MAVLink сообщений.

## Цель

Реализовать класс `MAVLinkValidator` в файле `src/validator.cpp`:

1. Проверка стартового байта (magic)
2. Проверка CRC (контрольной суммы)
3. Проверка sequence number
4. Валидация system_id и component_id

## Структура MAVLink v1 пакета

```
Offset  Size  Field
------  ----  -----
0       1     STX (Start of frame) = 0xFE
1       1     LEN (Payload length)
2       1     SEQ (Sequence number)
3       1     SYS (System ID)
4       1     COMP (Component ID)
5       1     MSG (Message ID)
6       LEN   PAYLOAD
6+LEN   2     CRC (Checksum, little-endian)
```

## CRC алгоритм

MAVLink использует X.25 CRC с дополнительным "CRC extra" байтом:

```cpp
uint16_t crc_accumulate(uint8_t data, uint16_t crc) {
    uint8_t tmp = data ^ (crc & 0xFF);
    tmp ^= (tmp << 4);
    return (crc >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4);
}

uint16_t crc_calculate(const uint8_t* data, size_t len, uint8_t crc_extra) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc = crc_accumulate(data[i], crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    return crc;
}
```

CRC считается для байтов с 1 по 5+LEN (включительно), плюс CRC_EXTRA.

## CRC Extra значения

Каждый тип сообщения имеет своё CRC_EXTRA значение:

| Message ID | Message Name       | CRC_EXTRA |
|------------|-------------------|-----------|
| 0          | HEARTBEAT         | 50        |
| 1          | SYS_STATUS        | 124       |
| 24         | GPS_RAW_INT       | 24        |
| 30         | ATTITUDE          | 39        |
| 33         | GLOBAL_POSITION_INT| 104      |
| 74         | VFR_HUD           | 20        |

## Что нужно реализовать

```cpp
// src/validator.h

enum class ValidationResult {
    Valid,
    InvalidMagic,
    InvalidLength,
    InvalidCRC,
    InvalidSequence,
    InvalidSystemId,
    UnknownMessageId
};

struct MAVLinkMessage {
    uint8_t magic;
    uint8_t length;
    uint8_t sequence;
    uint8_t system_id;
    uint8_t component_id;
    uint8_t message_id;
    std::vector<uint8_t> payload;
    uint16_t crc;
};

class MAVLinkValidator {
public:
    // Установить ожидаемый system_id (по умолчанию принимать любой)
    void setExpectedSystemId(uint8_t id);
    
    // Включить проверку sequence (по умолчанию выключена)
    void enableSequenceCheck(bool enable);
    
    // Парсинг сырых байтов в структуру
    std::optional<MAVLinkMessage> parse(const std::vector<uint8_t>& data);
    
    // Валидация сообщения
    ValidationResult validate(const MAVLinkMessage& msg);
    
    // Полная проверка: парсинг + валидация
    ValidationResult validateRaw(const std::vector<uint8_t>& data);
    
    // Получить последний валидный sequence number
    uint8_t getLastSequence() const;
    
    // Получить количество пропущенных сообщений
    uint32_t getMissedCount() const;
    
private:
    // TODO: добавьте необходимые поля
};
```

## Примеры

```cpp
#include "validator.h"

int main() {
    MAVLinkValidator validator;
    validator.setExpectedSystemId(1);
    validator.enableSequenceCheck(true);
    
    // Валидный HEARTBEAT пакет
    std::vector<uint8_t> packet = {
        0xFE,       // magic
        0x09,       // length = 9
        0x00,       // sequence
        0x01,       // system_id
        0x01,       // component_id
        0x00,       // message_id = HEARTBEAT
        // payload (9 bytes)
        0x00, 0x00, 0x00, 0x00,  // custom_mode
        0x02,                     // type
        0x03,                     // autopilot
        0x00,                     // base_mode
        0x03,                     // system_status
        0x03,                     // mavlink_version
        // CRC (little-endian)
        0xF4, 0x03
    };
    
    auto result = validator.validateRaw(packet);
    
    if (result == ValidationResult::Valid) {
        std::cout << "Packet is valid!" << std::endl;
    } else {
        std::cout << "Validation failed: " << static_cast<int>(result) << std::endl;
    }
    
    return 0;
}
```

## Структура проекта

```
src/
├── validator.h      # Заголовочный файл (готово)
├── validator.cpp    # Реализация (реализовать)
├── crc.h           # CRC функции (готово)
└── main.cpp        # Демо программа
tests/
└── test_validator.cpp  # Тесты
Makefile
```

## Сборка и запуск

```bash
cd easy/05-cpp-message-validator

# Сборка
make

# Запуск тестов
make test

# Запуск демо
./validator_demo
```

## Критерии оценки

- [ ] Корректный парсинг MAVLink пакетов
- [ ] Правильная проверка CRC
- [ ] Отслеживание sequence number
- [ ] Фильтрация по system_id
- [ ] Обработка невалидных данных
- [ ] Код проходит все тесты
- [ ] Нет утечек памяти

## Подсказки

1. Начните с парсинга — это самая простая часть
2. Для CRC используйте предоставленные функции в `crc.h`
3. Sequence идёт циклично 0-255, учитывайте переполнение
4. Используйте `std::optional` для возврата результата парсинга

## Дополнительно (необязательно)

- Поддержка MAVLink v2
- Статистика (количество валидных/невалидных пакетов)
- Многопоточность (thread-safe валидатор)
