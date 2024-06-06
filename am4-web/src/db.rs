use indexed_db_futures::{js_sys::Uint8Array, prelude::*};
use leptos::{logging::log, wasm_bindgen::{JsCast, JsValue}, web_sys};
use thiserror::Error;
use wasm_bindgen_futures::JsFuture;
use web_sys::{window, Response, js_sys::ArrayBuffer};
use am4::aircraft::db::Aircrafts;
use am4::airport::db::Airports;

pub struct Idb {
    database: IdbDatabase,
}

impl Idb {
    /// connect to the database and ensure that `am4help/static`` object store exists
    pub async fn connect() -> Result<Self, GenericError> {
        let mut db_req = IdbDatabase::open("am4help")?;
        db_req.set_on_upgrade_needed(Some(move |evt: &IdbVersionChangeEvent| {
            if !evt.db().object_store_names().any(|n| &n == "static") {
                evt.db().create_object_store("static")?;
            }
            Ok(())
        }));
        let db = db_req.await?;
        Ok(Self { database: db })
    }

    /// https://developer.mozilla.org/en-US/docs/Web/API/IDBObjectStore/put
    async fn write(&self, k: &str, v: &JsValue) -> Result<(), GenericError> {
        let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readwrite)?;
        let store = tx.object_store("static")?;

        store.put_key_val_owned(k, v)?;

        Ok(())
    }

    /// https://developer.mozilla.org/en-US/docs/Web/API/IDBObjectStore/get
    async fn get(&self, k: &str, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Option<JsValue>, GenericError> {
        let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readonly)?;
        let store = tx.object_store("static")?;
        
        set_progress(LoadDbProgress::IDBRead(k.to_string()));
        Ok(store.get_owned(k)?.await?)
    }

    pub async fn fetch(&self, k: &str, url: &str, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Vec<u8>, GenericError> {
        set_progress(LoadDbProgress::IDBCheck(k.to_string()));
        let ab = match self.get(k, set_progress).await? {
            Some(ab) => {
                assert!(ab.is_instance_of::<ArrayBuffer>());
                ab
            },
            None => {
                set_progress(LoadDbProgress::Fetching(k.to_string()));
                let ab = fetch_bytes(url).await?;
                set_progress(LoadDbProgress::IDBWrite(k.to_string()));
                self.write(k, &ab).await?;
                ab
            }
        };
        Ok(Uint8Array::new(&ab).to_vec())
    }

    pub async fn clear(&self) -> Result<(), GenericError> {
        let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readwrite)?;
        let store = tx.object_store("static")?;
        store.clear()?;
        Ok(())
    }

    pub async fn init_db(&self, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Database, GenericError> {
        // set_progress(LoadDbProgress::IDBConnect);
        // let db = Idb::connect().await?;
        
        let bytes = self.fetch("airports", "data/airports.bin", set_progress).await?;
        set_progress(LoadDbProgress::Parsing("airports".to_string()));
        let airports = Airports::from_bytes(&bytes).unwrap();
        log!("airports: {}", airports.data().len());
        
        let bytes = self.fetch("aircrafts", "data/aircrafts.bin", set_progress).await?;
        set_progress(LoadDbProgress::Parsing("aircrafts".to_string()));
        let aircrafts = Aircrafts::from_bytes(&bytes).unwrap();
        log!("aircrafts: {}", aircrafts.data().len());
        
        Ok(Database {
            aircrafts,
            airports,
        })
    }
}

async fn fetch_bytes(path: &str) -> Result<JsValue, GenericError> {
    log!("fetch: {path}");
    let window = window().unwrap();
    let resp_value = JsFuture::from(window.fetch_with_str(path)).await?;
    assert!(resp_value.is_instance_of::<Response>());

    let resp = resp_value.dyn_into::<Response>().unwrap();
    let data = JsFuture::from(resp.array_buffer()?).await?;
    assert!(data.is_instance_of::<ArrayBuffer>());

    Ok(data)
}

pub struct Database {
    pub aircrafts: Aircrafts,
    pub airports: Airports,
}

#[derive(Clone, PartialEq)]
pub enum LoadDbProgress {
    Starting,
    IDBConnect,
    IDBRead(String),
    IDBCheck(String),
    IDBWrite(String),
    Fetching(String),
    Parsing(String),
    Loaded,
    Err(GenericError)
}

#[derive(Clone, Error, Debug, PartialEq)]
pub enum GenericError {
    #[error("DOM exception: {:?}", self)]
    Dom(web_sys::DomException),
    #[error("JavaScript exception: {:?}", self)]
    Js(JsValue),
}

impl From<web_sys::DomException> for GenericError {
    fn from(dom_exception: web_sys::DomException) -> Self {
        Self::Dom(dom_exception)
    }
}

impl From<JsValue> for GenericError {
    fn from(js_value: JsValue) -> Self {
        Self::Js(js_value)
    }
}