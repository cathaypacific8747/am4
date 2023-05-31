#include <iostream>
#include <duckdb.hpp>
#include "include/airport.hpp"
#include "include/db.hpp"

using namespace std;
using namespace duckdb;

Airport Airport::from_id(int id) {
    // _query("SELECT * FROM airports WHERE id < 4;");
    Connection con = _get_connection();

    auto prep = con.Prepare("SELECT id FROM airports WHERE id < ?");
    if (!prep->success) {
        cout << prep->GetError() << endl;
    } else {
        cout << "success" << endl;
    }
    // auto result = prep->Execute(id);
    // result->Print();
    // auto data = result->Fetch();
    // cout << "col count: " << data->ColumnCount() << endl;

    // for (idx_t j = 0; j < data->ColumnCount(); j++) {
    //     cout << "col " << j << ": " << data->GetValue(j, 0) << endl;
    // }

    Airport ap;
    // ap.id = data->GetValue(0, 0).GetValue<uint16_t>();
    // ap.name = data->GetValue(1, 0).GetValue<string>();
    // ap.fullname = data->GetValue(2, 0).GetValue<string>();
    // ap.country = data->GetValue(3, 0).GetValue<string>();
    // ap.continent = data->GetValue(4, 0).GetValue<string>();
    // ap.iata = data->GetValue(5, 0).GetValue<string>();
    // ap.icao = data->GetValue(6, 0).GetValue<string>();
    // ap.lat = data->GetValue(7, 0).GetValue<double>();
    // ap.lng = data->GetValue(8, 0).GetValue<double>();
    // ap.rwy = data->GetValue(9, 0).GetValue<uint16_t>();
    // ap.market = data->GetValue(10, 0).GetValue<uint8_t>();
    // ap.hub_cost = data->GetValue(11, 0).GetValue<uint32_t>();
    // ap.rwy_codes = data->GetValue(12, 0).GetValue<string>();

    return ap;
}