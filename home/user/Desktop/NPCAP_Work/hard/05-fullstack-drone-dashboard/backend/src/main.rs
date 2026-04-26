//! Drone Dashboard Backend

mod api;
mod state;
mod mavlink;

use std::sync::Arc;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .with_env_filter("drone_dashboard_backend=debug,tower_http=debug")
        .init();
    
    tracing::info!("Starting Drone Dashboard Backend");
    
    // Create state manager
    let state = Arc::new(state::AppState::new());
    
    // TODO: Start MAVLink receiver
    // let mavlink_state = state.clone();
    // tokio::spawn(async move {
    //     mavlink::start_receiver("0.0.0.0:14550", mavlink_state).await;
    // });
    
    // Create router
    let app = api::create_router(state)
        .layer(TraceLayer::new_for_http())
        .layer(
            CorsLayer::new()
                .allow_origin(Any)
                .allow_methods(Any)
                .allow_headers(Any)
        );
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    tracing::info!("Listening on {}", listener.local_addr()?);
    
    axum::serve(listener, app).await?;
    
    Ok(())
}
