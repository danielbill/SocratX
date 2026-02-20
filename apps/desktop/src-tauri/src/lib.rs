use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            greet,
            chat,
            get_sessions,
            get_session,
            delete_session,
            get_memory,
            add_memory,
            get_config,
            update_config,
            get_tools,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

const BACKEND_URL: &str = "http://127.0.0.1:8000";

// ========== 命令 ==========

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn chat(message: String, session_id: String, user_id: String) -> Result<String, String> {
    let client = reqwest::Client::new();

    #[derive(Serialize)]
    struct ChatRequest {
        message: String,
        session_id: String,
        user_id: String,
    }

    let request = ChatRequest {
        message,
        session_id,
        user_id,
    };

    client
        .post(format!("{}/api/chat", BACKEND_URL))
        .json(&request)
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?
        .json::<serde_json::Value>()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))
        .and_then(|v| {
            v.get("content")
                .and_then(|c| c.as_str())
                .map(|s| s.to_string())
                .ok_or_else(|| "Missing content in response".to_string())
        })
}

#[tauri::command]
async fn get_sessions(user_id: Option<String>) -> Result<Vec<Session>, String> {
    let client = reqwest::Client::new();
    let uid = user_id.unwrap_or_else(|| "default".to_string());

    #[derive(Deserialize)]
    struct SessionListResponse {
        sessions: Vec<serde_json::Value>,
        total: i32,
    }

    let response = client
        .get(format!("{}/api/sessions?user_id={}", BACKEND_URL, uid))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?;

    let list_response: SessionListResponse = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    let mut sessions = Vec::new();
    for s in list_response.sessions {
        if let (Some(id), Some(user_id), Some(created_at), Some(updated_at)) = (
            s.get("id").and_then(|v| v.as_str()),
            s.get("user_id").and_then(|v| v.as_str()),
            s.get("created_at").and_then(|v| v.as_str()),
            s.get("updated_at").and_then(|v| v.as_str()),
        ) {
            sessions.push(Session {
                id: id.to_string(),
                user_id: user_id.to_string(),
                created_at: parse_timestamp(created_at),
                updated_at: parse_timestamp(updated_at),
            });
        }
    }

    Ok(sessions)
}

#[tauri::command]
async fn get_session(session_id: String) -> Result<Option<Session>, String> {
    let client = reqwest::Client::new();

    let response = client
        .get(format!("{}/api/sessions/{}", BACKEND_URL, session_id))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?;

    if response.status() == reqwest::StatusCode::NOT_FOUND {
        return Ok(None);
    }

    let s: serde_json::Value = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(Some(Session {
        id: s.get("id").and_then(|v| v.as_str()).unwrap_or("").to_string(),
        user_id: s.get("user_id").and_then(|v| v.as_str()).unwrap_or("").to_string(),
        created_at: s.get("created_at")
            .and_then(|v| v.as_str())
            .map(|ts| parse_timestamp(ts))
            .unwrap_or(0),
        updated_at: s.get("updated_at")
            .and_then(|v| v.as_str())
            .map(|ts| parse_timestamp(ts))
            .unwrap_or(0),
    }))
}

#[tauri::command]
async fn delete_session(session_id: String) -> Result<(), String> {
    let client = reqwest::Client::new();

    client
        .delete(format!("{}/api/sessions/{}", BACKEND_URL, session_id))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?;

    Ok(())
}

#[tauri::command]
async fn get_memory() -> Result<Memory, String> {
    let client = reqwest::Client::new();

    #[derive(Deserialize)]
    struct MemoryResponse {
        content: String,
    }

    let response: MemoryResponse = client
        .get(format!("{}/api/memory", BACKEND_URL))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(Memory {
        facts: vec![],
        history: vec![response.content],
    })
}

#[tauri::command]
async fn add_memory(content: String) -> Result<(), String> {
    let client = reqwest::Client::new();

    #[derive(Serialize)]
    struct MemoryRequest {
        content: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        section: Option<String>,
    }

    client
        .post(format!("{}/api/memory", BACKEND_URL))
        .json(&MemoryRequest {
            content,
            section: None,
        })
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?;

    Ok(())
}

#[tauri::command]
async fn get_config() -> Result<ConfigResponse, String> {
    let client = reqwest::Client::new();

    #[derive(Deserialize)]
    struct BackendConfigResponse {
        config: serde_json::Value,
    }

    let response: BackendConfigResponse = client
        .get(format!("{}/api/config", BACKEND_URL))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(ConfigResponse {
        config: response.config,
    })
}

#[tauri::command]
async fn update_config(updates: serde_json::Value) -> Result<(), String> {
    let client = reqwest::Client::new();

    #[derive(Serialize)]
    struct ConfigUpdateRequest {
        updates: serde_json::Value,
    }

    client
        .post(format!("{}/api/config", BACKEND_URL))
        .json(&ConfigUpdateRequest { updates })
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?;

    Ok(())
}

#[tauri::command]
async fn get_tools() -> Result<ToolsResponse, String> {
    let client = reqwest::Client::new();

    #[derive(Deserialize)]
    struct BackendToolsResponse {
        tools: Vec<serde_json::Value>,
        #[allow(dead_code)]
        count: i32,
    }

    let response: BackendToolsResponse = client
        .get(format!("{}/api/tools", BACKEND_URL))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to backend: {}", e))?
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    let tool_names: Vec<String> = response.tools
        .iter()
        .filter_map(|t| t.get("name").and_then(|n| n.as_str()).map(|s| s.to_string()))
        .collect();

    Ok(ToolsResponse {
        tools: tool_names,
    })
}

// ========== 辅助函数 ==========

fn parse_timestamp(s: &str) -> u64 {
    // Try parsing as ISO 8601, then as Unix timestamp
    if let Ok(dt) = chrono::DateTime::parse_from_rfc3339(s) {
        dt.timestamp() as u64
    } else if let Ok(ts) = s.parse::<u64>() {
        ts
    } else {
        chrono_timestamp()
    }
}

fn chrono_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

// ========== 类型定义 ==========

#[derive(Serialize)]
pub struct Session {
    pub id: String,
    pub user_id: String,
    pub created_at: u64,
    pub updated_at: u64,
}

#[derive(Serialize)]
pub struct Memory {
    pub facts: Vec<String>,
    pub history: Vec<String>,
}

#[derive(Serialize)]
pub struct ConfigResponse {
    pub config: serde_json::Value,
}

#[derive(Serialize)]
pub struct ToolsResponse {
    pub tools: Vec<String>,
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
        assert!(timestamp < 2000000000);
    }
}
