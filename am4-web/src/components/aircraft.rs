use crate::db::Database;
use am4::aircraft::db::AircraftSearchError;
use am4::aircraft::{Aircraft, AircraftType};
use leptos::{wasm_bindgen::JsCast, *};
use web_sys::HtmlInputElement;

#[component]
pub fn ACSearch() -> impl IntoView {
    let (search_term, set_search_term) = create_signal("".to_string());
    let database = expect_context::<StoredValue<Option<Database>>>();

    let search_results = move || {
        let s = search_term.get();
        database.with_value(|db| {
            db.as_ref()
                .unwrap()
                .aircrafts
                .search(s.as_str())
                .map_or_else(
                    |e| view! { <ACErr e/> },
                    |ac| view! { <Ac aircraft=ac.aircraft/> },
                )
        })
    };

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

            {search_results}
        </div>
    }
}

#[component]
fn ACErr(e: AircraftSearchError) -> impl IntoView {
    let database = expect_context::<StoredValue<Option<Database>>>();

    if let AircraftSearchError::AircraftNotFound(ctx) = &e {
        return database.with_value(|db| {
            let suggs = db.as_ref().unwrap().aircrafts.suggest_by_ctx(ctx);

            view! {
                <div>
                    <p class="err">"Aircraft not found. Did you mean: "</p>
                    <ul>

                        {suggs
                            .unwrap_or_default()
                            .into_iter()
                            .map(|sugg| {
                                view! {
                                    <li>{&sugg.item.shortname.0} " (" {&sugg.item.name.0} ")"</li>
                                }
                            })
                            .collect::<Vec<_>>()}

                    </ul>
                </div>
            }
        });
    } else if let AircraftSearchError::EmptyQuery = &e {
        return view! { <div></div> };
    }
    view! {
        <div class="err">
            <p>{e.to_string()}</p>
        </div>
    }
}

#[component]
fn Ac(aircraft: Aircraft) -> impl IntoView {
    let ac_type = move || match aircraft.ac_type {
        AircraftType::Pax => "Pax",
        AircraftType::Cargo => "Cargo",
        AircraftType::Vip => "VIP",
    };

    view! {
        <div class="ac-card">
            <h3>
                {&aircraft.manufacturer} " " {&aircraft.name.0} " ("
                <code>{&aircraft.shortname.0}</code> ", " {ac_type} ")"
            </h3>
            <table>
                <tr>
                    <th>{"Engine"}</th>
                    <td>{aircraft.ename} " (id: " {aircraft.eid} ")"</td>
                </tr>
                <tr>
                    <th>{"Speed"}</th>
                    <td>{aircraft.speed} " km/h (rank: " {format!("{}", aircraft.priority)} ")"</td>
                </tr>
                <tr>
                    <th>{"Priority"}</th>
                    <td>{format!("{}", aircraft.priority)}</td>
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
        </div>
    }
}
