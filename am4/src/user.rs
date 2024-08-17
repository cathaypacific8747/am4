use std::fmt;
use std::str::FromStr;
use thiserror::Error;
use uuid::Uuid;

#[derive(Debug, Clone, Error)]
pub enum UserError {
    #[error("Invalid wear training `{provided}`. Value must be between 0 and 5, inclusive.")]
    InvalidWearTraining { provided: u8 },
}

#[derive(Debug, Clone)]
pub struct Settings {
    pub game_mode: GameMode,
    pub wear_training: u8,
    pub repair_training: u8,
    pub l_training: u8,
    pub h_training: u8,
    pub fuel_training: u8,
    pub co2_training: u8,
    pub fuel_price: u16,
    pub co2_price: u8,
    pub accumulated_count: u16,
    pub load: f32,
    pub income_loss_tol: f32,
    pub fourx: bool,
}

#[derive(Debug, Clone)]
pub struct User {
    pub id: Uuid,
    pub username: String,
    pub game_id: u32,
    pub game_name: String,
    pub discord_id: u64,
    pub role: Role,
}

#[derive(Debug, Clone, PartialEq, Default)]
pub enum GameMode {
    #[default]
    Easy,
    Realism,
}

impl FromStr for GameMode {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "EASY" => Ok(Self::Easy),
            "REALISM" => Ok(Self::Realism),
            _ => Err(()),
        }
    }
}

#[derive(Debug, Clone)]
pub struct WearTraining(u8);

impl WearTraining {
    pub fn new(value: u8) -> Result<Self, UserError> {
        if value <= 5 {
            Ok(WearTraining(value))
        } else {
            Err(UserError::InvalidWearTraining { provided: value })
        }
    }

    pub fn get(&self) -> u8 {
        self.0
    }
}

impl TryFrom<u8> for WearTraining {
    type Error = UserError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        Self::new(value)
    }
}

impl fmt::Display for WearTraining {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

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

impl FromStr for Role {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "USER" => Ok(Self::User),
            "TRUSTED_USER" => Ok(Self::TrustedUser),
            "TRUSTED_USER_2" => Ok(Self::TrustedUser2),
            "TOP_ALLIANCE_MEMBER" => Ok(Self::TopAllianceMember),
            "TOP_ALLIANCE_ADMIN" => Ok(Self::TopAllianceAdmin),
            "HELPER" => Ok(Self::Helper),
            "MODERATOR" => Ok(Self::Moderator),
            "ADMIN" => Ok(Self::Admin),
            "GLOBAL_ADMIN" => Ok(Self::GlobalAdmin),
            _ => Err(()),
        }
    }
}
