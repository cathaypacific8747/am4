use leptos::*;

use crate::db::Database;

#[component]
#[allow(non_snake_case)]
pub fn Search(database: StoredValue<Option<Database>>) -> impl IntoView {
    let test = move || {
        database.with_value(|db| match db {
            Some(db) => {
                format!("{:?}", db.aircrafts.search("a388").unwrap())
            }
            None => unreachable!(),
        })
    };

    view! {
        <div id="search">
            <input type="text" placeholder="Search..."/>
        </div>
        <div>{test}</div>
    }
}
