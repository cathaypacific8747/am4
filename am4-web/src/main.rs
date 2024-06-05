mod db;
use db::init_db;
use leptos::*;

fn main() {
    console_error_panic_hook::set_once();
    leptos::mount_to_body(|| view! { <App/> })
}

#[component]
#[allow(non_snake_case)]
fn App() -> impl IntoView {
    // let (load_routes, _set_load_routes) = create_signal(false);

    let db = create_resource(|| (), |_| async move {
        match init_db().await {
            Ok(_) => "loaded".to_string(),
            Err(e) => e.to_string(),
        }
    });

    view! {
        <div>
            <code>"db"</code>
            ": "
            {move || db.get()}
        </div>
    }
}
