#[allow(non_snake_case)]
mod components;
mod db;

use components::nav::Header;
use components::aircraft::ACSearch;
use components::airport::APSearch;
use db::{Idb, Database, LoadDbProgress};

use leptos::*;
#[component]
#[allow(non_snake_case)]
pub fn App() -> impl IntoView {
    let database = store_value::<Option<Database>>(None);
    let (progress, set_progress) = create_signal(LoadDbProgress::Starting);

    provide_context(database);
    create_resource(
        || (),
        move |_| async move {
            set_progress.set(LoadDbProgress::IDBConnect);
            match Idb::connect().await.unwrap().init_db(&|msg| set_progress.set(msg)).await {
                Ok(db) => {
                    database.set_value(Some(db));
                    set_progress.set(LoadDbProgress::Loaded);
                }
                Err(e) => set_progress.set(LoadDbProgress::Err(e)),
            }
        },
    );

    view! {
        <div id="app">
            <Header progress/>
            <main>
                <Show when=move || progress.get() == LoadDbProgress::Loaded>
                    <ACSearch/>
                    <APSearch/>
                </Show>
            </main>
        </div>
    }
}