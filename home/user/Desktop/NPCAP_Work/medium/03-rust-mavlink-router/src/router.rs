//! Основная логика маршрутизатора.
//!
//! TODO: Реализуйте MAVLink роутер.


use crate::config::{Config, FilterConfig};
use crate::mavlink::MAVLinkMessage;
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::UdpSocket;
use tokio::sync::RwLock;

/// Входной канал.
pub struct Input {
    pub name: String,
    pub socket: Arc<UdpSocket>,
    pub system_id: Option<u8>,
}

/// Выходной канал.
pub struct Output {
    pub name: String,
    pub target: SocketAddr,
    pub socket: Arc<UdpSocket>,
}

/// Правило маршрутизации.
pub struct Route {
    pub from: String,
    pub to: Vec<String>,
    pub filter: FilterConfig,
}

/// Статистика роутера.
#[derive(Default)]
pub struct RouterStats {
    pub packets_received: u64,
    pub packets_routed: u64,
    pub packets_dropped: u64,
}

/// MAVLink Router.
pub struct Router {
    inputs: Vec<Input>,
    outputs: HashMap<String, Output>,
    routes: Vec<Route>,
    stats: Arc<RwLock<RouterStats>>,
}

impl Router {
    /// Создать роутер из конфигурации.
    ///
    /// TODO: Реализуйте создание роутера
    ///
    /// Шаги:
    /// 1. Для каждого input из конфига создать UDP сокет (UdpSocket::bind)
    /// 2. Для каждого output создать UDP сокет для отправки
    /// 3. Создать список Route из конфига
    pub async fn new(config: Config) -> Result<Self, Box<dyn std::error::Error>> {
    let mut inputs = Vec::new();
    for input_cfg in &config.inputs {
        let socket = UdpSocket::bind(&input_cfg.bind).await?;
        inputs.push(Input {
            name: input_cfg.name.clone(),
            socket: Arc::new(socket),
            system_id: input_cfg.system_id,
        });
    }

    let mut outputs = HashMap::new();
    for output_cfg in &config.outputs {
        // Создаём не привязанный сокет для отправки (bind на любой порт)
        let socket = UdpSocket::bind("0.0.0.0:0").await?;
        let target: SocketAddr = output_cfg.target.parse()?;
        outputs.insert(output_cfg.name.clone(), Output {
            name: output_cfg.name.clone(),
            target,
            socket: Arc::new(socket),
        });
    }

    let mut routes = Vec::new();
    for route_cfg in &config.routes {
        routes.push(Route {
            from: route_cfg.from.clone(),
            to: route_cfg.to.clone(),
            filter: route_cfg.filter.clone().unwrap_or_default(),
        });
    }

    Ok(Self {
        inputs,
        outputs,
        routes,
        stats: Arc::new(RwLock::new(RouterStats::default())),
    })
}
    
    /// Запустить роутер.
    ///
    /// TODO: Реализуйте основной цикл обработки пакетов
    ///
    /// Подсказка: используйте tokio::select! для обработки нескольких
    /// входных сокетов одновременно:
    ///
    /// ```ignore
    /// loop {
    ///     tokio::select! {
    ///         result = inputs[0].socket.recv_from(&mut buf) => {
    ///             let (len, addr) = result?;
    ///             self.handle_packet(&inputs[0].name, &buf[..len]).await?;
    ///         }
    ///         // ... другие inputs
    ///     }
    /// }
    /// ```
pub async fn run(self: Arc<Self>) -> Result<(), Box<dyn std::error::Error>> {
    tracing::info!("Router starting with {} inputs", self.inputs.len());

    let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel::<(String, Vec<u8>)>();

    // Запускаем по одной задаче на каждый входной сокет
    for input in &self.inputs {
        let socket = input.socket.clone();
        let name = input.name.clone();
        let tx = tx.clone();
        tokio::spawn(async move {
            let mut buf = vec![0u8; 2048];
            loop {
                match socket.recv_from(&mut buf).await {
                    Ok((len, _addr)) => {
                        let data = buf[..len].to_vec();
                        if tx.send((name.clone(), data)).is_err() {
                            tracing::warn!("Channel closed, stopping receive loop for {}", name);
                            break;
                        }
                    }
                    Err(e) => {
                        tracing::error!("Receive error on {}: {}", name, e);
                        break;
                    }
                }
            }
        });
    }
    drop(tx); // закрываем наш экземпляр, чтобы канал закрылся при завершении всех задач

    let ctrl_c = tokio::signal::ctrl_c();
    tokio::pin!(ctrl_c);

    loop {
        tokio::select! {
            Some((input_name, data)) = rx.recv() => {
                if let Err(e) = self.handle_packet(&input_name, &data).await {
                    tracing::error!("Error handling packet from {}: {}", input_name, e);
                }
            }
            _ = &mut ctrl_c => {
                tracing::info!("Received Ctrl+C, shutting down...");
                break;
            }
        }
    }

    Ok(())
}
    
    /// Обработать входящий пакет.
    ///
    /// TODO: Реализуйте обработку пакета
    ///
    /// Шаги:
    /// 1. Распарсить MAVLink сообщение
    /// 2. Обновить статистику packets_received
    /// 3. Найти подходящие маршруты через route()
    /// 4. Отправить пакет каждому получателю
    /// 5. Обновить статистику packets_routed
async fn handle_packet(
    &self,
    input_name: &str,
    data: &[u8],
) -> Result<(), Box<dyn std::error::Error>> {
    // 1. Парсинг MAVLink сообщения
    let msg = match MAVLinkMessage::parse(data) {
        Ok(m) => m,
        Err(e) => {
            tracing::warn!("Failed to parse MAVLink packet from {}: {}", input_name, e);
            let mut stats = self.stats.write().await;
            stats.packets_dropped += 1;
            return Ok(());
        }
    };

    // 2. Проверка CRC
    if !msg.validate_crc() {
        tracing::warn!("Invalid CRC for packet from {}", input_name);
        let mut stats = self.stats.write().await;
        stats.packets_dropped += 1;
        return Ok(());
    }

    // 3. Обновление статистики полученных пакетов
    {
        let mut stats = self.stats.write().await;
        stats.packets_received += 1;
    }

    // 4. Поиск подходящих выходов
    let outputs = self.route(input_name, &msg);

    // 5. Сериализация сообщения (один раз для всех получателей)
    let bytes = msg.to_bytes();

    // 6. Отправка и обновление статистики
    for output in outputs {
        match output.socket.send_to(&bytes, output.target).await {
            Ok(_) => {
                let mut stats = self.stats.write().await;
                stats.packets_routed += 1;
            }
            Err(e) => {
                tracing::warn!("Failed to send to {} ({}): {}", output.name, output.target, e);
                let mut stats = self.stats.write().await;
                stats.packets_dropped += 1;
            }
        }
    }

    Ok(())
}
    
    /// Найти выходные каналы для сообщения.
    ///
    /// TODO: Реализуйте логику маршрутизации
    ///
    /// Для каждого route проверьте:
    /// 1. Совпадает ли route.from с input_name
    /// 2. Проходит ли сообщение фильтр (matches_filter)
    /// 3. Если да — добавьте все outputs из route.to в результат
fn route(&self, input_name: &str, msg: &MAVLinkMessage) -> Vec<&Output> {
    let mut result = Vec::new();
    for route in &self.routes {
        if route.from == input_name && self.matches_filter(msg, &route.filter) {
            for out_name in &route.to {
                if let Some(output) = self.outputs.get(out_name) {
                    result.push(output);
                } else {
                    tracing::warn!("Output '{}' not found in route from '{}'", out_name, input_name);
                }
            }
        }
    }
    result
}

fn matches_filter(&self, msg: &MAVLinkMessage, filter: &FilterConfig) -> bool {
    // Если нет фильтрации по message_id и system_id, пропускаем всё
    let message_ids_match = match &filter.message_ids {
        Some(ids) => ids.contains(&msg.message_id),
        None => true,
    };
    let system_ids_match = match &filter.system_ids {
        Some(ids) => ids.contains(&msg.system_id),
        None => true,
    };
    message_ids_match && system_ids_match
}
    
    /// Получить статистику.
    pub async fn get_stats(&self) -> RouterStats {
        self.stats.read().await.clone()
    }
}

impl Clone for RouterStats {
    fn clone(&self) -> Self {
        Self {
            packets_received: self.packets_received,
            packets_routed: self.packets_routed,
            packets_dropped: self.packets_dropped,
        }
    }
}
