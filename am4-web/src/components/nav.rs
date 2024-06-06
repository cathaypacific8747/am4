use crate::db::{LoadDbProgress, Idb};
use leptos::{*, logging::log};

static VERSION: &'static str = env!("CARGO_PKG_VERSION");

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
            LoadDbProgress::Loaded => write!(f, ""),
            LoadDbProgress::Err(e) => write!(f, "error: {}", e.to_string()),
        }
    }
}

#[component]
#[allow(non_snake_case)]
pub fn Header(progress: ReadSignal<LoadDbProgress>) -> impl IntoView {
    let prog_str = move || progress.get().to_string();

    let clear_db = create_action(|_e| {
        log!("clear cache");
        async move {
            Idb::connect().await.unwrap().clear().await.unwrap();
        }
    });

    view! {
        <header role="banner">
            <div id="global-nav">
                <a href="https://github.com/cathaypacific8747/am4" target="_blank">
                    <img src="/assets/img/logo-64.webp" alt="logo" height="32" width="32"/>
                </a>
                <div>
                    <span id="name">AM4Help</span>
                    <span id="version">" v" {VERSION}</span>
                </div>
                <div id="db-progress">{prog_str}</div>
            </div>
            <div id="local-bar">
                <nav>
                    <ul>
                        <li>
                            <b>
                                <a href="/">"Home"</a>
                            </b>
                        </li>
                        <li>
                            <a href="https://cathaypacific8747.github.io/am4/formulae/">
                                "Formulae"
                            </a>
                        </li>
                        <Show when=move || progress.get() == LoadDbProgress::Loaded>
                            <li
                                id="clear-cache"
                                on:click=move |ev| {
                                    clear_db.dispatch(ev);
                                }
                            >

                                "Clear Cache"
                            </li>
                        </Show>
                    </ul>
                </nav>
            </div>
        </header>
    }
}
