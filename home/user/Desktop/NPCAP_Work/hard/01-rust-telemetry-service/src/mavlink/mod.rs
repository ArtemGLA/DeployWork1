//! MAVLink module.
//! 
//! TODO: Реализуйте парсер и приёмник MAVLink сообщений

pub mod parser;
pub mod receiver;

pub use parser::MAVLinkMessage;
pub use receiver::MAVLinkReceiver;
