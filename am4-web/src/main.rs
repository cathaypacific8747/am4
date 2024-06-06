use am4_web::App;
use leptos::*;

fn main() {
    console_error_panic_hook::set_once();

    leptos::mount_to_body(|| view! { <App/> })
}
