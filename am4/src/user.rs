use std::str::FromStr;
use uuid::Uuid;

#[derive(Debug, Clone, PartialEq)]
pub enum GameMode {
    Easy,
    Realism,
}

impl Default for GameMode {
    fn default() -> Self {
        Self::Easy
    }
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

#[derive(Debug, Clone, PartialEq)]
pub enum Role {
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

impl Default for Role {
    fn default() -> Self {
        Self::User
    }
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
