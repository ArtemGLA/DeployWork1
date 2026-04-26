//! Telemetry Service - микросервис телеметрии БПЛА.

mod config;
mod error;
mod mavlink;
mod state;
mod api;

use clap::Parser;
use std::sync::Arc;
use tokio::signal;

#[derive(Parser)]
#[command(name = "telemetry-service")]
#[command(about = "MAVLink telemetry microservice")]
struct Args {
    /// MAVLink UDP port
    #[arg(long, default_value = "14550")]
    mavlink_port: u16,
    
    /// HTTP server port
    #[arg(long, default_value = "8080")]
    http_port: u16,
    
    /// Config file path
    #[arg(short, long)]
    config: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Инициализация логирования
    tracing_subscriber::fmt()
        .with_env_filter("telemetry_service=debug,tower_http=debug")
        .init();
    
    let args = Args::parse();
    
    tracing::info!("Starting Telemetry Service");
    tracing::info!("MAVLink port: {}", args.mavlink_port);
    tracing::info!("HTTP port: {}", args.http_port);
    
    // Создание state manager
    let state_manager = Arc::new(state::StateManager::new());
    
    // TODO: Создание MAVLink receiver
    // let mavlink_receiver = mavlink::MAVLinkReceiver::new(
    //     &format!("0.0.0.0:{}", args.mavlink_port),
    //     state_manager.clone(),
    // ).await?;
    
    // Создание HTTP сервера
    let app = api::create_router(state_manager.clone());
    
    let listener = tokio::net::TcpListener::bind(
        format!("0.0.0.0:{}", args.http_port)
    ).await?;
    
    tracing::info!("HTTP server listening on {}", listener.local_addr()?);
    
    // Запуск сервера с graceful shutdown
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;
    
    tracing::info!("Service stopped");
    
    Ok(())
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("Failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("Failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    tracing::info!("Shutdown signal received");
}
