//! Конфигурация роутера.

use serde::Deserialize;
use std::path::Path;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub inputs: Vec<InputConfig>,
    pub outputs: Vec<OutputConfig>,
    pub routes: Vec<RouteConfig>,
}

#[derive(Debug, Deserialize)]
pub struct InputConfig {
    pub name: String,
    #[serde(rename = "type")]
    pub input_type: String,
    pub bind: String,
    pub system_id: Option<u8>,
}

#[derive(Debug, Deserialize)]
pub struct OutputConfig {
    pub name: String,
    #[serde(rename = "type")]
    pub output_type: String,
    pub target: String,
}

#[derive(Debug, Deserialize)]
pub struct RouteConfig {
    pub from: String,
    pub to: Vec<String>,
    pub filter: Option<FilterConfig>,
}

#[derive(Debug, Deserialize, Default, Clone)]
pub struct FilterConfig {
    pub message_ids: Option<Vec<u8>>,
    pub system_ids: Option<Vec<u8>>,
}

impl Config {
    /// Загрузить конфигурацию из YAML файла.
    pub fn load(path: &Path) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let config: Config = serde_yaml::from_str(&content)?;
        Ok(config)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parse_config() {
        let yaml = r#"
inputs:
  - name: drone1
    type: udp
    bind: "0.0.0.0:14550"
    system_id: 1

outputs:
  - name: gcs1
    type: udp
    target: "127.0.0.1:14600"

routes:
  - from: drone1
    to: [gcs1]
    filter:
      message_ids: [0, 33]
"#;
        
        let config: Config = serde_yaml::from_str(yaml).unwrap();
        
        assert_eq!(config.inputs.len(), 1);
        assert_eq!(config.outputs.len(), 1);
        assert_eq!(config.routes.len(), 1);
        assert_eq!(config.inputs[0].name, "drone1");
    }
}
