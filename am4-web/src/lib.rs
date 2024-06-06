mod nav;
mod search;
mod db;

use nav::Header;
use search::Search;
use db::{init_db, Database, LoadDbProgress};

use leptos::*;
#[component]
#[allow(non_snake_case)]
pub fn App() -> impl IntoView {
    let database = store_value::<Option<Database>>(None);
    let (progress, set_progress) = create_signal(LoadDbProgress::Starting);

    create_resource(
        || (),
        move |_| async move {
            match init_db(&|msg| set_progress.set(msg)).await {
                Ok(db) => {
                    database.set_value(Some(db));
                    set_progress.set(LoadDbProgress::Loaded);
                }
                Err(e) => set_progress.set(LoadDbProgress::Err(e)),
            }
        },
    );

    let status = move || {
        if progress.get() == LoadDbProgress::Loaded {
            database.with_value(|db| match db {
                Some(db) => {
                    format!("{:?}", db.aircrafts.search("a388").unwrap())
                }
                None => unreachable!(),
            })
        } else {
            "".to_string()
        }
    };

    view! {
        <div id="app">
            <Header progress/>
            <Show when=move || progress.get() == LoadDbProgress::Loaded>
                <Search database/>
            </Show>
        </div>
    }
}