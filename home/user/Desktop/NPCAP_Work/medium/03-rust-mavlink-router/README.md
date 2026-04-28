# Задание 3: MAVLink Router

**Уровень:** Средний  
**Технологии:** Rust, tokio  
**Время выполнения:** 5-7 часов

## Описание

MAVLink Router — это сервис, который принимает MAVLink сообщения из нескольких источников и перенаправляет их получателям по заданным правилам. Это позволяет подключать несколько GCS к одному дрону или агрегировать данные с нескольких дронов.

## Цель

Реализовать асинхронный MAVLink маршрутизатор, который:

1. Принимает UDP пакеты с нескольких портов
2. Парсит MAVLink сообщения
3. Применяет правила фильтрации
4. Пересылает сообщения получателям

## Архитектура

```
                          ┌─────────────────┐
Drone 1 ──UDP:14550──────▶│                 │
                          │                 │──UDP:14600──▶ GCS 1
Drone 2 ──UDP:14551──────▶│  MAVLink Router │
                          │                 │──UDP:14601──▶ GCS 2
Drone 3 ──UDP:14552──────▶│                 │
                          └─────────────────┘
```

## Конфигурация

```yaml
# config.yaml
inputs:
  - name: drone1
    type: udp
    bind: "0.0.0.0:14550"
    system_id: 1
    
  - name: drone2
    type: udp
    bind: "0.0.0.0:14551"
    system_id: 2

outputs:
  - name: gcs1
    type: udp
    target: "127.0.0.1:14600"
    
  - name: gcs2
    type: udp
    target: "127.0.0.1:14601"

routes:
  - from: drone1
    to: [gcs1, gcs2]
    filter:
      message_ids: [0, 1, 24, 30, 33, 74]  # heartbeat, sys_status, gps, attitude, position, vfr_hud
      
  - from: drone2
    to: [gcs1]
    filter:
      message_ids: [0, 33]  # только heartbeat и position
```

## Что нужно реализовать

### Основные структуры

```rust
pub struct Router {
    inputs: Vec<Input>,
    outputs: Vec<Output>,
    routes: Vec<Route>,
}

pub struct Input {
    name: String,
    socket: UdpSocket,
    system_id: Option<u8>,
}

pub struct Output {
    name: String,
    target: SocketAddr,
    socket: UdpSocket,
}

pub struct Route {
    from: String,
    to: Vec<String>,
    filter: MessageFilter,
}

pub struct MessageFilter {
    message_ids: Option<Vec<u8>>,
    system_ids: Option<Vec<u8>>,
}
```

### Основные функции

```rust
impl Router {
    /// Загрузить конфигурацию
    pub async fn from_config(path: &str) -> Result<Self>;
    
    /// Запустить роутер
    pub async fn run(&mut self) -> Result<()>;
    
    /// Обработать входящий пакет
    async fn handle_packet(&self, input_name: &str, data: &[u8]) -> Result<()>;
    
    /// Применить правила маршрутизации
    fn route(&self, input_name: &str, msg: &MAVLinkMessage) -> Vec<&Output>;
    
    /// Проверить фильтр
    fn matches_filter(&self, msg: &MAVLinkMessage, filter: &MessageFilter) -> bool;
}
```

### MAVLink парсер

```rust
pub struct MAVLinkMessage {
    pub magic: u8,
    pub length: u8,
    pub sequence: u8,
    pub system_id: u8,
    pub component_id: u8,
    pub message_id: u8,
    pub payload: Vec<u8>,
    pub crc: u16,
}

impl MAVLinkMessage {
    /// Парсить MAVLink пакет из байтов
    pub fn parse(data: &[u8]) -> Result<Self>;
    
    /// Проверить CRC
    pub fn validate_crc(&self) -> bool;
    
    /// Сериализовать обратно в байты
    pub fn to_bytes(&self) -> Vec<u8>;
}
```

## Запуск

```bash
cd medium/03-rust-mavlink-router

# Сборка
cargo build --release

# Запуск с конфигурацией
cargo run -- --config config.yaml

# Тесты
cargo test
```

## Тестирование

Используйте эмулятор из `common/mavlink-emulator`:

```bash
# Терминал 1: запуск роутера
cargo run -- --config config.yaml

# Терминал 2: запуск эмулятора (дрон 1)
python ../../common/mavlink-emulator/emulator.py --send-only --host 127.0.0.1 --port 14550 --rate 5 --auto-arm

# Терминал 3: приём данных (GCS)
nc -u -l 14600
```

## Критерии оценки

- [ ] Корректный парсинг MAVLink пакетов
- [ ] Загрузка конфигурации из YAML
- [ ] Асинхронная обработка нескольких входов
- [ ] Правильная маршрутизация по правилам
- [ ] Фильтрация по message_id и system_id
- [ ] Обработка ошибок без паники
- [ ] Код проходит все тесты

## Подсказки

1. Используйте `tokio::select!` для обработки нескольких источников
2. Для YAML используйте `serde_yaml`
3. Для парсинга MAVLink — либо свой код, либо crate `mavlink`
4. Используйте `Arc<RwLock>` для shared state если нужно
5. Логирование через `tracing` или `log`

## Дополнительно (необязательно)

- Поддержка TCP соединений
- Статистика (количество сообщений, пропускная способность)
- Hot reload конфигурации
- Web UI для мониторинга
