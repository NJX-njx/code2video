// 后端管理模块
// 负责启动/停止 FastAPI 后端 + Next.js 前端服务进程

use serde::Serialize;
use std::process::{Command, Stdio};

/// 后端进程状态
#[derive(Debug, Serialize, Clone)]
pub struct BackendStatus {
    pub running: bool,
    pub pid: Option<u32>,
    pub port: u16,
}

/// 启动 FastAPI 后端（端口 8000）
#[tauri::command]
pub async fn start_backend() -> Result<BackendStatus, String> {
    let child = Command::new("conda")
        .args([
            "run", "-n", "mathvideo", "--no-banner",
            "python", "-u", "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
        ])
        .current_dir(get_project_root())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("无法启动后端: {}", e))?;

    let pid = child.id();

    Ok(BackendStatus {
        running: true,
        pid: Some(pid),
        port: 8000,
    })
}

/// 停止 FastAPI 后端
#[tauri::command]
pub async fn stop_backend() -> Result<BackendStatus, String> {
    #[cfg(target_os = "windows")]
    {
        // Windows: 通过 netstat 查找并终止端口 8000 上的进程
        let _ = Command::new("powershell")
            .args([
                "-Command",
                "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            ])
            .output();
    }

    #[cfg(not(target_os = "windows"))]
    {
        let _ = Command::new("sh")
            .args(["-c", "lsof -ti:8000 | xargs kill -9 2>/dev/null"])
            .output();
    }

    Ok(BackendStatus {
        running: false,
        pid: None,
        port: 8000,
    })
}

/// 检查后端是否在运行（通过 /health 端点）
#[tauri::command]
pub async fn get_backend_status() -> Result<BackendStatus, String> {
    let client = reqwest::Client::new();
    match client
        .get("http://localhost:8000/health")
        .timeout(std::time::Duration::from_secs(2))
        .send()
        .await
    {
        Ok(resp) if resp.status().is_success() => Ok(BackendStatus {
            running: true,
            pid: None,
            port: 8000,
        }),
        _ => Ok(BackendStatus {
            running: false,
            pid: None,
            port: 8000,
        }),
    }
}

/// 获取项目根目录
fn get_project_root() -> String {
    if cfg!(debug_assertions) {
        // 开发模式：从 frontend/ 上溯到项目根目录
        let cwd = std::env::current_dir().unwrap_or_default();
        if cwd.ends_with("frontend") {
            cwd.parent()
                .unwrap_or(&cwd)
                .to_string_lossy()
                .to_string()
        } else {
            cwd.to_string_lossy().to_string()
        }
    } else {
        // 生产模式：可执行文件所在目录即项目根目录
        std::env::current_exe()
            .ok()
            .and_then(|p| p.parent().map(|p| p.to_path_buf()))
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_else(|| ".".to_string())
    }
}
