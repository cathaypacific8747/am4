use indexed_db_futures::prelude::*;
use leptos::{logging::log, wasm_bindgen::{prelude::*, JsValue}, web_sys};
use thiserror::Error;
use wasm_bindgen_futures::JsFuture;
use web_sys::{window, Response, js_sys::{Uint8Array, Array}, Blob, BlobPropertyBag};
use am4::aircraft::db::Aircrafts;
use am4::airport::{Airport, db::Airports};
use am4::route::db::Distances;
use am4::{AC_FILENAME, AP_FILENAME, DIST_FILENAME};

pub struct Idb {
    database: IdbDatabase,
}

// TODO: replace unwrap with proper handling with rkvy parse errors.
impl Idb {
    /// connect to the database and ensure that `am4help/data` object store exists
    pub async fn connect() -> Result<Self, GenericError> {
        let mut db_req = IdbDatabase::open("am4help")?;
        db_req.set_on_upgrade_needed(Some(move |evt: &IdbVersionChangeEvent| {
            if !evt.db().object_store_names().any(|n| &n == "data") {
                evt.db().create_object_store("data")?;
            }
            Ok(())
        }));
        let db = db_req.await?;
        Ok(Self { database: db })
    }

    async fn get(&self, k: &str) -> Result<Option<JsValue>, GenericError> {
        let tx = self.database.transaction_on_one_with_mode("data", IdbTransactionMode::Readonly)?;
        tx.object_store("data")?.get_owned(k)?.await.map_err(|e| e.into())
    }

    async fn write(&self, k: &str, v: &JsValue) -> Result<(), GenericError> {
        let tx = self.database.transaction_on_one_with_mode("data", IdbTransactionMode::Readwrite).unwrap();
        tx.object_store("data")?.put_key_val_owned(k, v)?;
        Ok(())
    }

    pub async fn clear(&self) -> Result<(), GenericError> {
        let tx = self.database.transaction_on_one_with_mode("data", IdbTransactionMode::Readwrite)?;
        tx.object_store("data")?.clear()?;
        Ok(())
    }

    /// Load a binary file from the IndexedDb. If the blob is not found*, 
    /// fetch it from the server and cache it in the IndexedDb.
    /// not found: `Response`* -> `Blob`* -> IndexedDb -> `Blob` -> `ArrayBuffer` -> `Vec<u8>`
    pub async fn get_blob(&self, k: &str, url: &str, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Vec<u8>, GenericError> {
        set_progress(LoadDbProgress::IDBRead(k.to_string()));
        let jsb = match self.get(k).await? {
            Some(b) => b,
            None => {
                set_progress(LoadDbProgress::Fetching(k.to_string()));
                let b = fetch_bytes(url).await?;
                set_progress(LoadDbProgress::IDBWrite(k.to_string()));
                let _ = self.write(k, &b).await;
                b
            }
        };
        let ab = JsFuture::from(jsb.dyn_into::<Blob>()?.array_buffer()).await?;
        Ok(Uint8Array::new(&ab).to_vec())
    }

    /// Load the flat distances from the indexeddb. If the blob is not found*,
    /// generate it from the slice of airports and cache it in the indexeddb.
    /// not found: `&[Airport]`* -> `Distances`* (return this) -> `Blob`* -> IndexedDb
    /// found: IndexedDb -> `Blob` -> `ArrayBuffer` -> `Distances`
    async fn get_distances(&self, aps: &[Airport], set_progress: &dyn Fn(LoadDbProgress)) -> Result<Distances, GenericError> {
        let k = DIST_FILENAME;
        set_progress(LoadDbProgress::IDBRead(k.to_string()));
        match self.get(k).await? {
            Some(jsb) => {
                set_progress(LoadDbProgress::Parsing(k.to_string()));
                let ab = JsFuture::from(jsb.dyn_into::<Blob>()?.array_buffer()).await?;
                let bytes = Uint8Array::new(&ab).to_vec();
                Ok(Distances::from_bytes(&bytes).unwrap())
            },
            None => {
                set_progress(LoadDbProgress::Parsing(k.to_string()));
                let distances = Distances::from_airports(aps);
                let b = distances.to_bytes().unwrap();
                
                // https://github.com/rustwasm/wasm-bindgen/issues/1693
                // effectively, this is `new Blob([new Uint8Array(b)], {type: 'application/octet-stream'})`
                let ja = Array::new();
                ja.push(&Uint8Array::from(b.as_slice()).buffer());
                let mut opts = BlobPropertyBag::new();
                opts.type_("application/octet-stream");
                let blob = Blob::new_with_u8_array_sequence_and_options(&ja, &opts)?;
                let _ = self.write(k, &blob).await;
                Ok(distances)
            }
        }
    }

    pub async fn init_db(&self, set_progress: &dyn Fn(LoadDbProgress)) -> Result<Database, GenericError> {
        let bytes = self.get_blob(AP_FILENAME, format!("data/{}", AP_FILENAME).as_str(), set_progress).await?;
        set_progress(LoadDbProgress::Parsing("airports".to_string()));
        let airports = Airports::from_bytes(&bytes).unwrap();
        log!("airports: {}", airports.data().len());
        
        let bytes = self.get_blob(AC_FILENAME, format!("data/{}", AC_FILENAME).as_str(), set_progress).await?;
        set_progress(LoadDbProgress::Parsing("aircrafts".to_string()));
        let aircrafts = Aircrafts::from_bytes(&bytes).unwrap();
        log!("aircrafts: {}", aircrafts.data().len());
        
        set_progress(LoadDbProgress::Parsing("distances".to_string()));
        let distances = self.get_distances(airports.data(), set_progress).await?;
        log!("distances: {}", distances.data().len());
        // let distances = Distances::from_airports(&(airports.data()));
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