// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_os::init())
        .setup(|app| {
            use tauri::Manager;
            
            #[cfg(target_os = "macos")]
            {
                if let Some(window) = app.get_webview_window("main") {
                    // macOS: 启用原生装饰和 overlay 标题栏样式
                    window.set_decorations(true).ok();
                    use tauri::TitleBarStyle;
                    window.set_title_bar_style(TitleBarStyle::Overlay).ok();
                }
            }
            
            #[cfg(not(target_os = "macos"))]
            {
                // Windows/Linux: 保持无装饰
                if let Some(window) = app.get_webview_window("main") {
                    window.set_decorations(false).ok();
                }
            }
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
