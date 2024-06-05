use indexed_db_futures::{js_sys::Uint8Array, prelude::*};
use leptos::{logging::log, wasm_bindgen::{JsCast, JsValue}, web_sys};
use thiserror::Error;
use wasm_bindgen_futures::JsFuture;
use web_sys::{window, Response, js_sys::ArrayBuffer};
use am4::airport::db::Airports;
use am4::aircraft::db::Aircrafts;
use am4::route::db::Routes;

pub struct Db {
    database: IdbDatabase,
}

impl Db {
    /// connect to the database and ensure that `am4help/static`` object store exists
    async fn connect() -> Result<Self, GenericError> {
        let mut db_req = IdbDatabase::open("am4help")?;
        db_req.set_on_upgrade_needed(Some(move |evt: &IdbVersionChangeEvent| {
            if let None = evt.db().object_store_names().find(|n| n == "static") {
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
    async fn get(&self, k: &str) -> Result<Option<JsValue>, GenericError> {
        log!("idb(read): {k}");
        let tx = self.database.transaction_on_one_with_mode("static", IdbTransactionMode::Readonly)?;
        let store = tx.object_store("static")?;

        Ok(store.get_owned(k)?.await?)
    }

    pub async fn fetch(&self, k: &str, url: &str) -> Result<Vec<u8>, GenericError> {
        let ab = match self.get(k).await? {
            Some(ab) => {
                assert!(ab.is_instance_of::<ArrayBuffer>());
                ab
            },
            None => {
                let ab = fetch_bytes(url).await?;
                self.write(k, &ab).await?;
                ab
            }
        };
        Ok(Uint8Array::new(&ab).to_vec())
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


pub async fn init_db() -> Result<String, GenericError> {
    let db = Db::connect().await?;
    
    let bytes = db.fetch("airports", "data/airports.bin").await?;
    let aps = Airports::from_bytes(&bytes).unwrap();
    log!("airports: {}", aps.data().len());
    
    let bytes = db.fetch("aircrafts", "data/aircrafts.bin").await?;
    let acs = Aircrafts::from_bytes(&bytes).unwrap();
    log!("aircrafts: {}", acs.data().len());
    
    let bytes = db.fetch("routes", "data/routes.bin").await?;
    let rts = Routes::from_bytes(&bytes).unwrap();
    log!("routes: {}", rts.data().len());

    Ok("Done!".to_string())
}

#[derive(Error, Debug)]
pub enum GenericError {
    #[error("DOM exception: {}", self.to_string())]
    Dom(web_sys::DomException),
    #[error("JavaScript exception: {}", self.to_string())]
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