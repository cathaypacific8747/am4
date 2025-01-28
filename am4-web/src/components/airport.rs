// use crate::db::Data;
use am4::airport::db::AirportSearchError;
use am4::airport::Airport;
use leptos::prelude::*;
use leptos::{wasm_bindgen::JsCast, *};
use web_sys::HtmlInputElement;

#[allow(non_snake_case)]
#[component]
pub fn APSearch() -> impl IntoView {
    let (_search_term, set_search_term) = signal("".to_string());

    // let database = expect_context::<StoredValue<Option<Data>>>();
    // let search_results = move || {
    //     let s = search_term.get();
    //     database.with_value(|db| {
    //         db.as_ref()
    //             .unwrap()
    //             .airports
    //             .search(s.as_str())
    //             .map_or_else(|e| view! { <APErr e/> }, |ap| view! { <Ap airport=ap/> })
    //     })
    // };

    view! {
        <div id="ap-search">
            <input
                type="text"
                placeholder="Search an airport..."
                on:input=move |event| {
                    let target = event.target().unwrap();
                    let value = target.unchecked_into::<HtmlInputElement>().value();
                    set_search_term.set(value);
                }
            />

        // <div>{search_results}</div>
        </div>
    }
}

#[allow(non_snake_case)]
#[component]
fn APErr(_e: AirportSearchError) -> impl IntoView {
    // let database = expect_context::<StoredValue<Option<Data>>>();

    // if let AirportSearchError::AirportNotFound(ctx) = &e {
    //     return database.with_value(|db| {
    //         let suggs = db.as_ref().unwrap().airports.suggest_by_ctx(ctx);

    //         view! {
    //             <div>
    //                 <p>"Airport not found. Did you mean: "</p>
    //                 <ul>

    //                     {suggs
    //                         .unwrap_or_default()
    //                         .into_iter()
    //                         .map(|sugg| {
    //                             view! {
    //                                 <li>
    //                                     {&sugg.item.iata.to_string()} " / "
    //                                     {&sugg.item.icao.to_string()} " ("
    //                                     {&sugg.item.name.to_string()} ", " {&sugg.item.country} ")"
    //                                 </li>
    //                             }
    //                         })
    //                         .collect::<Vec<_>>()}

    //                 </ul>
    //             </div>
    //         }
    //     });
    // } else if let AirportSearchError::EmptyQuery = &e {
    //     return view! { <div></div> };
    // }
    // view! {
    //     <div>
    //         <p>{e.to_string()}</p>
    //     </div>
    // }
    view! { <div>"Under construction"</div> }
}

#[allow(dead_code)] // leptos bug
#[allow(non_snake_case)]
#[component]
fn Ap<'a>(airport: &'a Airport) -> impl IntoView {
    view! {
        <div class="ap-card">
            <h3>
                {airport.name.to_string()} ", " {airport.country.to_string()} " ("
                {airport.iata.to_string()} " / " {airport.icao.to_string()} ")"
            </h3>
            <table>
                <tr>1 <th>"Full Name"</th> <td>{airport.fullname.to_string()}</td></tr>
                <tr>
                    <th>"Continent"</th>
                    <td>{airport.continent.to_string()}</td>
                </tr>
                <tr>
                    <th>"Location"</th>
                    <td>{format!("{}, {}", &airport.location.lat, &airport.location.lng)}</td>
                </tr>
                <tr>
                    <th>"Runway"</th>
                    <td>{format!("{}", &airport.rwy)}</td>
                </tr>
                <tr>
                    <th>"Market"</th>
                    <td>{format!("{}", &airport.market)}</td>
                </tr>
                <tr>
                    <th>"Hub Cost"</th>
                    <td>{format!("{}", &airport.hub_cost)}</td>
                </tr>
                <tr>
                    <th>"Runway Codes"</th>
                    <td>{airport.rwy_codes.join(",")}</td>
                </tr>
            </table>
        </div>
    }
}
