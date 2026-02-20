#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            greet,
            send_message,
            create_session,
            get_sessions,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn send_message(message: String, _session_id: String) -> Result<String, String> {
    // TODO: Call Python service
    Ok(format!("Echo: {}", message))
}

#[tauri::command]
async fn create_session() -> Result<String, String> {
    // Generate a simple session ID
    Ok(format!("session_{}", chrono_timestamp()))
}

#[tauri::command]
async fn get_sessions() -> Result<Vec<Session>, String> {
    Ok(vec![])
}

fn chrono_timestamp() -> i64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0)
}

#[derive(serde::Serialize)]
struct Session {
    id: String,
    messages: Vec<Message>,
}

#[derive(serde::Serialize)]
struct Message {
    role: String,
    content: String,
    timestamp: String,
}

// ========== 测试模块 ==========

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        let result = greet("Alice");
        assert_eq!(result, "Hello, Alice! You've been greeted from Rust!");
    }

    #[test]
    fn test_greet_empty_name() {
        let result = greet("");
        assert_eq!(result, "Hello, ! You've been greeted from Rust!");
    }

    #[test]
    fn test_chrono_timestamp() {
        let timestamp = chrono_timestamp();
        assert!(timestamp > 0);
        assert!(timestamp < 2000000000); // 合理的 timestamp 范围
    }
}
