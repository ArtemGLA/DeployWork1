//! MAVLink Router - маршрутизатор MAVLink сообщений.

mod config;
mod mavlink;
mod router;

use clap::Parser;
use std::path::PathBuf;
use std::sync::Arc;

#[derive(Parser)]
#[command(name = "mavlink-router")]
#[command(about = "MAVLink message router")]
struct Args {
    /// Path to configuration file
    #[arg(short, long, default_value = "config.yaml")]
    config: PathBuf,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Инициализация логирования
    tracing_subscriber::fmt::init();
    
    let args = Args::parse();
    
    tracing::info!("Loading config from {:?}", args.config);
    
    let config = config::Config::load(&args.config)?;
    
    tracing::info!(
        "Configured {} inputs, {} outputs, {} routes",
        config.inputs.len(),
        config.outputs.len(),
        config.routes.len()
    );
    
    let mut router = router::Router::new(config).await?;
    
    tracing::info!("Starting router...");

    let router = Arc::new(router); //ADD УДАЛИИИИ
    
    router.run().await?;
    
    Ok(())
}
