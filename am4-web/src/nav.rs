use crate::db::LoadDbProgress;
use leptos::*;

impl std::fmt::Display for LoadDbProgress {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LoadDbProgress::Starting => write!(f, "starting"),
            LoadDbProgress::IDBConnect => write!(f, "idb(connect)"),
            LoadDbProgress::IDBRead(key) => write!(f, "idb(read): {}", key),
            LoadDbProgress::IDBCheck(key) => write!(f, "idb(check): {}", key),
            LoadDbProgress::IDBWrite(key) => write!(f, "idb(write): {}", key),
            LoadDbProgress::Fetching(key) => write!(f, "fetch: {}", key),
            LoadDbProgress::Parsing(key) => write!(f, "parse: {}", key),
            LoadDbProgress::Loaded => write!(f, "Routes not loaded."),
            LoadDbProgress::Err(e) => write!(f, "error: {}", e.to_string()),
        }
    }
}

#[component]
#[allow(non_snake_case)]
pub fn Header(progress: ReadSignal<LoadDbProgress>) -> impl IntoView {
    let prog_str = move || progress.get().to_string();

    view! {
        <div id="header">
            <div id="global-nav">
                <img src="/assets/img/logo-64.webp" alt="logo" height="32" width="32"/>
                <div>AM4Help <sup>" v0.0.1"</sup></div>
                <div id="db-progress">{prog_str}</div>
            </div>
            <div id="local-bar">
                <nav>
                    <ul>
                        <li>
                            <a href="/ac">"Research"</a>
                        </li>
                        <li>
                            <a href="/ap">"Manage"</a>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    }
}
