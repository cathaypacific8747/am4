#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod app;
use eframe::egui;

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([800.0, 600.0]),
        ..Default::default()
    };
    eframe::run_native(
        "am4help",
        options,
        Box::new(|cc| Box::new(app::AM4Help::new(cc))),
    )?;

    Ok(())
}
