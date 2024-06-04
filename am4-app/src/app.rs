use am4::aircraft::db::{Aircrafts, AircraftsIndex};
use am4::airport::db::{Airports, AirportsIndex};
use eframe::{egui, CreationContext};
use std::fs::File;
use std::io::Read;

use once_cell::sync::Lazy;

static AIRPORTS: Lazy<Airports> =
    Lazy::new(|| Airports::from_bytes(&get_bytes("am4/data/airports.bin").unwrap()).unwrap());

static AIRCRAFTS: Lazy<Aircrafts> =
    Lazy::new(|| Aircrafts::from_bytes(&get_bytes("am4/data/aircrafts.bin").unwrap()).unwrap());

pub struct AM4Help<'a> {
    search_mode: SearchMode,
    search_query: String,
    search_results: String,
    ap_idx: AirportsIndex<'a>,
    ac_idx: AircraftsIndex<'a>,
}

#[derive(PartialEq)]
enum SearchMode {
    Airport,
    Aircraft,
}

pub fn get_bytes(path: &str) -> Result<Vec<u8>, std::io::Error> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::<u8>::new();
    file.read_to_end(&mut buffer)?;
    Ok(buffer)
}

impl<'a> AM4Help<'a> {
    pub fn new(_cc: &CreationContext<'_>) -> Self {
        Self {
            search_mode: SearchMode::Airport,
            search_query: String::new(),
            search_results: "Search results will appear here.".to_owned(),
            ac_idx: AircraftsIndex::new(&AIRCRAFTS),
            ap_idx: AirportsIndex::new(&AIRPORTS),
        }
    }
}

impl<'a> eframe::App for AM4Help<'a> {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("AM4Help");

            ui.horizontal(|ui| {
                ui.radio_value(&mut self.search_mode, SearchMode::Airport, "Airports");
                ui.radio_value(&mut self.search_mode, SearchMode::Aircraft, "Aircraft");
            });

            ui.horizontal(|ui| {
                ui.label("Search: ");
                if ui.text_edit_singleline(&mut self.search_query).changed() {
                    self.search_results = match self.search_mode {
                        SearchMode::Airport => search_airport(&self.search_query, &self.ap_idx),
                        SearchMode::Aircraft => search_aircraft(&self.search_query, &self.ac_idx),
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

fn search_airport(query: &str, index: &AirportsIndex) -> String {
    match index.search(query) {
        Ok(airport) => format!("{:#?}", airport),
        Err(err) => match index.suggest(query) {
            Ok(suggestions) => format!("Error: {}\nSuggestions: {:#?}", err, suggestions),
            Err(err) => format!("Error: {:?}", err),
        },
    }
}

fn search_aircraft(query: &str, index: &AircraftsIndex) -> String {
    match index.search(query) {
        Ok(aircraft) => format!("{:#?}", aircraft),
        Err(err) => match index.suggest(query) {
            Ok(suggestions) => format!("Error: {}\nSuggestions: {:#?}", err, suggestions),
            Err(err) => format!("Error: {:?}", err),
        },
    }
}
