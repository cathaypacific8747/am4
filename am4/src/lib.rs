//! Core tools and utilities for the game Airline Manager 4.

pub mod airport;
pub mod utils;

pub mod campaign;
pub mod ticket;
pub mod user;

pub mod aircraft;

pub mod route; // under development

// to keep track of changes for data files in `../data`
#[macro_export]
macro_rules! ac_version {
    () => {
        "2"
    };
}
pub const AC_FILENAME: &str = concat!("aircrafts-v", ac_version!(), ".bin");

#[macro_export]
macro_rules! ap_version {
    () => {
        "0"
    };
}
pub const AP_FILENAME: &str = concat!("airports-v", ap_version!(), ".bin");
// distances are generated from the airports
pub const DIST_FILENAME: &str = concat!("distances-v", ap_version!(), ".bin");

#[macro_export]
macro_rules! demand_version {
    () => {
        "0"
    };
}
pub const DEM_FILENAME0: &str = concat!("demands0-v", demand_version!(), ".bin");
pub const DEM_FILENAME1: &str = concat!("demands1-v", demand_version!(), ".bin");
