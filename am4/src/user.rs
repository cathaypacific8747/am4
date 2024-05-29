use std::str::FromStr;

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

#[derive(Debug, Clone, Default)]
pub struct User {
    pub id: String,
    pub username: String,
    pub game_id: u32,
    pub game_name: String,
    pub game_mode: GameMode,
    pub discord_id: u64,
    pub wear_training: u8,
    pub repair_training: u8,
    pub l_training: u8,
    pub h_training: u8,
    pub fuel_training: u8,
    pub co2_training: u8,
    pub fuel_price: u16,
    pub co2_price: u8,
    pub accumulated_count: u16,
    pub load: f64,
    pub income_loss_tol: f64,
    pub fourx: bool,
    pub role: Role,
}

impl User {
    pub fn new(realism: bool) -> Self {
        let mut user = Self::default();
        if realism {
            user.id = "00000000-0000-0000-0000-000000000001".to_string();
            user.game_mode = GameMode::Realism;
        }
        user
    }
}
