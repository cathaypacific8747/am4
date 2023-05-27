from __future__ import annotations

import am4utils

def test():
    ey0 = am4utils.optimal_y_easy_price(10000)
    e = am4utils.create_pax_ticket(10000, True)
    assert ey0 == e.y_price == 4580