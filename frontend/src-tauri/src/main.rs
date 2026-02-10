// MathVideo Tauri 桌面应用入口
// 管理 Python 后端生命周期 + 环境检测

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod env_checker;
mod backend_manager;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .invoke_handler(tauri::generate_handler![
            env_checker::check_environment,
            env_checker::get_conda_envs,
            backend_manager::start_backend,
            backend_manager::stop_backend,
            backend_manager::get_backend_status,
        ])
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("启动 MathVideo 失败");
}
