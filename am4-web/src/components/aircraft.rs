use crate::db::Data;
use am4::aircraft::db::{AircraftSearchError, LENGTH_MAX, LENGTH_MEAN};
use am4::aircraft::Aircraft;
use leptos::prelude::*;
use leptos::wasm_bindgen::JsCast;
use web_sys::HtmlInputElement;

#[allow(non_snake_case)]
#[component]
pub fn ACSearch() -> impl IntoView {
    let (search_term, set_search_term) = signal("".to_string());
    let database = expect_context::<StoredValue<Option<Data>>>();

    // let search_results = move || {
    //     let s = search_term.get();
    //     database.with_value(|db| {
    //         db.as_ref()
    //             .unwrap()
    //             .aircrafts
    //             .search(s.as_str())
    //             .map_or_else(
    //                 |e| view! { <ACErr e/> },
    //                 |ac| view! { <Ac aircraft=ac.aircraft/> },
    //             )
    //     })
    // };

    view! {
        <div id="ac-search">
            <input
                type="text"
                placeholder="Search an aircraft..."
                on:input=move |event| {
                    let target = event.target().unwrap();
                    let value = target.unchecked_into::<HtmlInputElement>().value();
                    set_search_term.set(value);
                }
            />

        // {search_results}
        </div>
    }
}

#[allow(non_snake_case)]
#[component]
fn ACErr(e: AircraftSearchError) -> impl IntoView {
    let database = expect_context::<StoredValue<Option<Data>>>();

    // if let AircraftSearchError::AircraftNotFound(ctx) = &e {
    //     return database.with_value(|db| {
    //         let suggs = db.as_ref().unwrap().aircrafts.suggest_by_ctx(ctx);

    //         view! {
    //             <div>
    //                 <p class="err">"Aircraft not found. Did you mean: "</p>
    //                 <ul>

    //                     {suggs
    //                         .unwrap_or_default()
    //                         .into_iter()
    //                         .map(|sugg| {
    //                             view! {
    //                                 <li>
    //                                     {sugg.item.shortname.to_string()} " ("
    //                                     {sugg.item.name.to_string()} ")"
    //                                 </li>
    //                             }
    //                         })
    //                         .collect::<Vec<_>>()}

    //                 </ul>
    //             </div>
    //         }
    //     });
    // } else if let AircraftSearchError::EmptyQuery = &e {
    //     return view! { <div></div> };
    // }
    // view! {
    //     <div class="err">
    //         <p>{e.to_string()}</p>
    //     </div>
    // }
    view! { <div>"An error occurred"</div> }
}

#[allow(non_snake_case)]
#[component]
fn Ac(aircraft: Aircraft) -> impl IntoView {
    let width = if aircraft.length == 0 {
        LENGTH_MEAN / LENGTH_MAX
    } else {
        aircraft.length as f32 / LENGTH_MAX
    } * 250f32;

    view! {
        <div class="ac-card">
            <h3>
                {aircraft.manufacturer} " " {aircraft.name.to_string()} " ("
                <code>{aircraft.shortname.to_string()}</code> ", " {aircraft.r#type.to_string()} ")"
            </h3>
            <table>
                <tr>
                    <th>{"Engine"}</th>
                    <td>
                        {aircraft.ename} " (id: " {aircraft.eid} ", rank: "
                        {format!("{}", aircraft.priority)} ")"
                    </td>
                </tr>
                <tr>
                    <th>{"Speed"}</th>
                    <td>{aircraft.speed} " km/h"</td>
                </tr>
                <tr>
                    <th>{"Fuel"}</th>
                    <td>{aircraft.fuel} " lbs/km"</td>
                </tr>
                <tr>
                    <th>{"CO2"}</th>
                    <td>{aircraft.co2} " kg/pax/km"</td>
                </tr>
                <tr>
                    <th>{"Cost"}</th>
                    <td>"$ " {aircraft.cost}</td>
                </tr>
                <tr>
                    <th>{"Capacity"}</th>
                    <td>{aircraft.capacity}</td>
                </tr>
                <tr>
                    <th>{"Range"}</th>
                    <td>{aircraft.range} " km"</td>
                </tr>
                <tr>
                    <th>{"Runway"}</th>
                    <td>{aircraft.rwy} " ft"</td>
                </tr>
                <tr>
                    <th>{"Check cost"}</th>
                    <td>"$ " {aircraft.check_cost}</td>
                </tr>
                <tr>
                    <th>{"Maintenance"}</th>
                    <td>{aircraft.maint} " hr"</td>
                </tr>
                <tr>
                    <th>{"Ceiling"}</th>
                    <td>{aircraft.ceil} " ft"</td>
                </tr>
                <tr>
                    <th>{"Personnel"}</th>
                    <td>
                        {format!(
                            "{} pilots, {} crew, {} engineers, {} technicians",
                            aircraft.pilots,
                            aircraft.crew,
                            aircraft.engineers,
                            aircraft.technicians,
                        )}

                    </td>
                </tr>
                <tr>
                    <th>{"Dimensions"}</th>
                    <td>{format!("{} m × {} m", aircraft.length, aircraft.wingspan)}</td>
                </tr>
            </table>
            <div id="ac-img">
                <img src=format!("/assets/img/aircraft/{}.webp", aircraft.img) width=width/>
            </div>
        </div>
    }
}
