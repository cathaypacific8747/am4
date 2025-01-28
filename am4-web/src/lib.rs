mod components;
mod console;
mod db;

// use components::aircraft::ACSearch;
// use components::airport::APSearch;
use components::nav::Header;

use console::{Entry, Level};
// use db::Idb;
use leptos::{logging::log, prelude::*};
use reactive_stores::Store;

#[component]
#[allow(non_snake_case)]
pub fn App() -> impl IntoView {
    let database = StoredValue::<Option<db::Data>>::new(None);
    let console = Store::new(console::Console { history: vec![] });

    provide_context(database);
    provide_context(console);

    Resource::new(
        || (),
        move |_| async move {
            console.write().history.push(Entry {
                time: 0,
                level: Level::Debug,
                user: "system".to_string(),
                message: "start".to_string(),
            });
            let history = console
                .get()
                .history
                .iter()
                .map(|m| m.message.as_str())
                .collect::<Vec<_>>()
                .join("\n");
            log!("{history}");
            // let db = Idb::connect().await;
            // match Idb::connect()
            //     .await
            //     .unwrap()
            //     .init_db()
            //     .await
            // {
            //     Ok(db) => {
            //         database.set_value(Some(db));
            //     }
            //     Err(e) => {
            //         log!("{e}");
            //         set_progress.set(LoadDbProgress::Err);
            //     },
            // }
        },
    );

    view! {
        <div id="app">
            <Header/>
            // <Show when=move || progress.read() == db::LoadDbProgress::Loaded>
            // <ACSearch/>
            // <APSearch/>
            // </Show>
            <main></main>
        </div>
    }
}
