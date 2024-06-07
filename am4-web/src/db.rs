use indexed_db_futures::prelude::*;
use leptos::{logging::log, wasm_bindgen::{prelude::*, JsValue}, web_sys};
use thiserror::Error;
use wasm_bindgen_futures::JsFuture;
use web_sys::{window, Response, js_sys::{Uint8Array}, Blob};
use am4::aircraft::db::Aircrafts;
use am4::airport::db::Airports;
// use am4::route::db::Routes;

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

    /// Load a binary file from the IndexedDb. If the blob is not found*, fetch it from the server
    /// and cache it in the IndexedDb.
    /// `Response`* -> `Blob`* -> IndexedDb -> `Blob` -> `ArrayBuffer` -> `Vec<u8>`
    /// https://developer.mozilla.org/en-US/docs/Web/API/IDBObjectStore/put
    pub async fn fetch(&self, k: &str, url: &str, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Vec<u8>, GenericError> {
        set_progress(LoadDbProgress::IDBRead(k.to_string()));
        let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readonly)?;
        let jsb = tx.object_store("static")?.get_owned(k)?.await?;
        
        let jsb = match jsb {
            Some(b) => b,
            None => {
                set_progress(LoadDbProgress::Fetching(k.to_string()));
                let b = fetch_bytes(url).await?;
                set_progress(LoadDbProgress::IDBWrite(k.to_string()));
                let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readwrite)?;
                tx.object_store("static")?.put_key_val_owned(k, &b)?;
                b
            }
        };
        let ab = JsFuture::from(jsb.dyn_into::<Blob>()?.array_buffer()).await?;
        Ok(Uint8Array::new(&ab).to_vec())
    }

    pub async fn clear(&self) -> Result<(), GenericError> {
        let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readwrite)?;
        let store = tx.object_store("static")?;
        store.clear()?;
        Ok(())
    }

    pub async fn init_db(&self, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Database, GenericError> {
        let bytes = self.fetch("airports", "data/airports.bin", set_progress).await?;
        set_progress(LoadDbProgress::Parsing("airports".to_string()));
        let airports = Airports::from_bytes(&bytes).unwrap();
        log!("airports: {}", airports.data().len());
        
        let bytes = self.fetch("aircrafts", "data/aircrafts.bin", set_progress).await?;
        set_progress(LoadDbProgress::Parsing("aircrafts".to_string()));
        let aircrafts = Aircrafts::from_bytes(&bytes).unwrap();
        log!("aircrafts: {}", aircrafts.data().len());
        
        // let bytes = self.fetch("routes", "data/routes.bin", set_progress).await?;
        // set_progress(LoadDbProgress::Parsing("routes".to_string()));
        // let routes = Routes::from_bytes(&bytes).unwrap();
        // log!("routes: {}", routes.data().len());

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
    let resp = resp_value.dyn_into::<Response>()?;
    let jsb = JsFuture::from(resp.blob()?).await?;
    Ok(jsb)
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