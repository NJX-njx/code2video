// 环境检测模块
// 检查 conda / mathvideo 环境 / ffmpeg 等依赖是否就绪

use serde::Serialize;
use std::process::Command;

/// 环境检测结果
#[derive(Debug, Serialize, Clone)]
pub struct EnvStatus {
    pub conda_installed: bool,
    pub conda_version: Option<String>,
    pub mathvideo_env_exists: bool,
    pub python_version: Option<String>,
    pub ffmpeg_installed: bool,
    pub ffmpeg_version: Option<String>,
    pub all_ready: bool,
}

/// 检测所有依赖环境
#[tauri::command]
pub async fn check_environment() -> Result<EnvStatus, String> {
    let conda = check_conda().await;
    let env_exists = if conda.0 {
        check_mathvideo_env().await
    } else {
        false
    };
    let python_ver = if env_exists {
        check_python_version().await
    } else {
        None
    };
    let ffmpeg = check_ffmpeg().await;

    let all_ready = conda.0 && env_exists && python_ver.is_some() && ffmpeg.0;

    Ok(EnvStatus {
        conda_installed: conda.0,
        conda_version: conda.1,
        mathvideo_env_exists: env_exists,
        python_version: python_ver,
        ffmpeg_installed: ffmpeg.0,
        ffmpeg_version: ffmpeg.1,
        all_ready,
    })
}

/// 获取 conda 环境列表
#[tauri::command]
pub async fn get_conda_envs() -> Result<Vec<String>, String> {
    let output = Command::new("conda")
        .args(["info", "--envs"])
        .output()
        .map_err(|e| format!("无法执行 conda: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let envs: Vec<String> = stdout
        .lines()
        .filter(|line| !line.starts_with('#') && !line.trim().is_empty())
        .filter_map(|line| {
            let parts: Vec<&str> = line.split_whitespace().collect();
            parts.first().map(|s| s.to_string())
        })
        .collect();

    Ok(envs)
}

/// 检查 conda 是否安装
async fn check_conda() -> (bool, Option<String>) {
    match Command::new("conda").args(["--version"]).output() {
        Ok(output) => {
            let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
            (output.status.success(), Some(version))
        }
        Err(_) => (false, None),
    }
}

/// 检查 mathvideo conda 环境是否存在
async fn check_mathvideo_env() -> bool {
    match Command::new("conda")
        .args(["run", "-n", "mathvideo", "--no-banner", "python", "--version"])
        .output()
    {
        Ok(output) => output.status.success(),
        Err(_) => false,
    }
}

/// 获取 mathvideo 环境的 Python 版本
async fn check_python_version() -> Option<String> {
    Command::new("conda")
        .args(["run", "-n", "mathvideo", "--no-banner", "python", "--version"])
        .output()
        .ok()
        .and_then(|output| {
            if output.status.success() {
                Some(String::from_utf8_lossy(&output.stdout).trim().to_string())
            } else {
                None
            }
        })
}

/// 检查 ffmpeg 是否安装
async fn check_ffmpeg() -> (bool, Option<String>) {
    match Command::new("ffmpeg").args(["-version"]).output() {
        Ok(output) => {
            let version = String::from_utf8_lossy(&output.stdout)
                .lines()
                .next()
                .unwrap_or("")
                .to_string();
            (output.status.success(), Some(version))
        }
        Err(_) => (false, None),
    }
}
