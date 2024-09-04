use std::sync::LazyLock;

use derive_more::derive::{Constructor, Display, From, Into};
use thiserror::Error;
use uuid::Uuid;

#[derive(Debug, Clone, Error)]
pub enum ValidationError {
    #[error("invalid wear training, must be between 0 and 5 (inclusive)")]
    InvalidWearTraining,
    #[error("invalid repair training, must be between 0 and 5 (inclusive)")]
    InvalidRepairTraining,
    #[error("invalid large training, must be between 0 and 6 (inclusive)")]
    InvalidLargeTraining,
    #[error("invalid heavy training, must be between 0 and 6 (inclusive)")]
    InvalidHeavyTraining,
    #[error("invalid fuel training, must be between 0 and 3 (inclusive)")]
    InvalidFuelTraining,
    #[error("invalid co2 training, must be between 0 and 5 (inclusive)")]
    InvalidCo2Training,
    #[error("invalid aircraft load, must be between 0.1 and 1.5")]
    InvalidAircraftLoad,
    #[error("invalid income loss tolerance, must be between 0.0 and 1.0")]
    InvalidIncomeLossTol,
}

// TODO: escape strings to avoid injection attacks
#[derive(Debug, Clone)]
pub struct User {
    pub id: Uuid,
    pub username: String,
    pub game_id: u32,
    pub game_name: String,
    pub discord_id: u64,
    pub role: Role,
    // NOTE: intentionally not putting in settings to avoid duplicates in
    // AbstractRoutes vs. ScheduledRoutes
    pub game_mode: GameMode,
}

#[derive(Debug, Clone, Default)]
pub struct Settings {
    pub training: Training,
    pub fuel_price: FuelPrice,
    pub co2_price: Co2Price,
    pub accumulated_count: u16,
    pub load: AircraftLoad,
    pub income_loss_tol: f32,
    pub fourx: bool,
}

static DEFAULT_SETTINGS: LazyLock<Settings> = LazyLock::new(Settings::default);

impl<'a> Default for &'a Settings {
    fn default() -> Self {
        &DEFAULT_SETTINGS
    }
}

// TODO: impl FromStr for fuel and co2

/// The assumed fuel price, for use in profit calculations
#[derive(Debug, Clone, Copy, PartialEq, From, Into, Constructor)]
pub struct FuelPrice(u16);

/// The assumed CO₂, for use in profit calculations
#[derive(Debug, Clone, Copy, PartialEq, From, Into, Constructor)]
pub struct Co2Price(u16);

#[derive(Debug, Clone, PartialEq, Default)]
pub enum GameMode {
    #[default]
    Easy,
    Realism,
}

#[derive(Debug, Clone, Default)]
pub struct Training {
    pub wear: WearTraining,
    pub repair: RepairTraining,
    pub large: LargeTraining,
    pub heavy: HeavyTraining,
    pub fuel: FuelTraining,
    pub co2: Co2Training,
}

macro_rules! create_newtype {
    ($name:ident, $inner_type:ty) => {
        #[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Display, Into)]
        pub struct $name($inner_type);
    };
}

macro_rules! impl_constructor {
    ($name:ident, $inner_type:ty, $condition:expr, $err_variant:ident) => {
        impl $name {
            #[doc = "Creates a new value with bounds checking."]
            pub fn new(value: $inner_type) -> Result<Self, ValidationError> {
                if $condition(value) {
                    Ok(Self(value))
                } else {
                    Err(ValidationError::$err_variant)
                }
            }
        }

        impl TryFrom<$inner_type> for $name {
            type Error = ValidationError;

            fn try_from(value: $inner_type) -> Result<Self, Self::Error> {
                Self::new(value)
            }
        }
    };
}

macro_rules! impl_default {
    ($name:ident, $default_value:expr) => {
        impl Default for $name {
            #[doc = concat!("Returns the default value of `", stringify!($default_value), "`")]
            fn default() -> Self {
                Self($default_value)
            }
        }
    };
}

macro_rules! create_validated_newtype {
    ($name:ident, $inner_type:ty, $condition:expr, $err_variant:ident, $default_value:expr) => {
        create_newtype!($name, $inner_type);
        impl_constructor!($name, $inner_type, $condition, $err_variant);
        impl_default!($name, $default_value);
    };
}

impl_default!(FuelPrice, 900);
impl_default!(Co2Price, 120);
create_validated_newtype!(
    AircraftLoad,
    f32,
    |v: f32| v.is_finite() && (0.1..=1.5).contains(&v),
    InvalidAircraftLoad,
    0.99
);
create_validated_newtype!(
    IncomeLossTol,
    f32,
    |v: f32| v.is_finite() && (0.0..=1.0).contains(&v),
    InvalidIncomeLossTol,
    0.0
);
create_validated_newtype!(WearTraining, u8, |v| v < 5, InvalidWearTraining, 0);
create_validated_newtype!(RepairTraining, u8, |v| v < 5, InvalidRepairTraining, 0);
create_validated_newtype!(LargeTraining, u8, |v| v < 6, InvalidLargeTraining, 0);
create_validated_newtype!(HeavyTraining, u8, |v| v < 6, InvalidHeavyTraining, 0);
create_validated_newtype!(FuelTraining, u8, |v| v < 3, InvalidFuelTraining, 0);
create_validated_newtype!(Co2Training, u8, |v| v < 5, InvalidCo2Training, 0);

#[derive(Debug, Clone, PartialEq, Default)]
pub enum Role {
    #[default]
    User,
    TrustedUser,
    TrustedUser2,
    TopAllianceMember,
    TopAllianceAdmin,
    Helper,
    Moderator,
    Admin,
    GlobalAdmin,
}
