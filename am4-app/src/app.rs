use am4::aircraft::search::Aircrafts;
use am4::airport::search::Airports;
use eframe::{egui, CreationContext};

pub struct AM4Help {
    search_mode: SearchMode,
    search_query: String,
    search_results: String,
    data: AppData,
}

#[derive(PartialEq)]
enum SearchMode {
    Airport,
    Aircraft,
}

struct AppData {
    airports: Airports,
    aircrafts: Aircrafts,
}

impl AM4Help {
    pub fn new(_cc: &CreationContext<'_>) -> Self {
        let airports = Airports::from_csv("am4/data/airports.csv").unwrap();
        let aircrafts = Aircrafts::from_csv("am4/data/aircrafts.csv").unwrap();

        Self {
            search_mode: SearchMode::Airport,
            search_query: String::new(),
            search_results: "Search results will appear here.".to_owned(),
            data: AppData {
                airports,
                aircrafts,
            },
        }
    }
}

impl eframe::App for AM4Help {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("AM4Help");

            ui.horizontal(|ui| {
                ui.radio_value(&mut self.search_mode, SearchMode::Airport, "Airports");
                ui.radio_value(&mut self.search_mode, SearchMode::Aircraft, "Aircraft");
            });

            ui.horizontal(|ui| {
                ui.label("Search: ");
                // Update results on text change
                if ui.text_edit_singleline(&mut self.search_query).changed() {
                    self.search_results = match self.search_mode {
                        SearchMode::Airport => {
                            search_airport(&self.search_query, &self.data.airports)
                        }
                        SearchMode::Aircraft => {
                            search_aircraft(&self.search_query, &self.data.aircrafts)
                        }
                    };
                }
            });

            egui::ScrollArea::vertical().show(ui, |ui| {
                ui.text_edit_multiline(&mut self.search_results);
            });
        });

        ctx.request_repaint();
    }
}

fn search_airport(query: &str, index: &Airports) -> String {
    match index.search(query) {
        Ok(airport) => format!("{:#?}", airport),
        Err(err) => match index.suggest(query) {
            Ok(suggestions) => format!("Error: {}\nSuggestions: {:#?}", err, suggestions),
            Err(err) => format!("Error: {:?}", err),
        },
    }
}

fn search_aircraft(query: &str, index: &Aircrafts) -> String {
    match index.search(query) {
        Ok(aircraft) => format!("{:#?}", aircraft),
        Err(err) => match index.suggest(query) {
            Ok(suggestions) => format!("Error: {}\nSuggestions: {:#?}", err, suggestions),
            Err(err) => format!("Error: {:?}", err),
        },
    }
}
