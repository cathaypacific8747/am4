use reactive_stores::Store;

#[allow(dead_code)]
#[derive(Debug, Clone, Default)]
pub enum Level {
    #[default]
    Debug,
    Info,
    Success,
}

#[derive(Debug, Clone, Store)]
pub struct Entry {
    pub time: u64,
    pub level: Level,
    pub user: String,
    pub message: String,
}

#[derive(Debug, Clone, Store)]
pub struct Console {
    pub history: Vec<Entry>,
}
