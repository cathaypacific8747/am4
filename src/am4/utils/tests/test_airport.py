import pytest

from am4.utils.airport import Airport


@pytest.mark.parametrize(
    "inp",
    [
        "id:3500",
        "iata:Hkg",
        "icao:vhhh",
        "name:hong kong",
        "fullname:hong kong, hong kong",
        "hong kong",
        "hong kong, hong kong",
    ],
)
def test_airport_search(inp):
    a0 = Airport.search(inp)
    assert a0.ap.valid
    assert a0.ap.iata == "HKG"


@pytest.mark.parametrize(
    "inp",
    [
        "VHHX  ",
        "iata:hkgA",
        "icao:VHHx",
        "name:hng kong",
    ],
)
def test_airport_fail_and_suggest(inp):
    a0 = Airport.search(inp)
    assert not a0.ap.valid
    suggs = Airport.suggest(a0.parse_result)
    assert suggs[0].ap.iata == "HKG"


@pytest.mark.parametrize("inp", ["65590", "id:65590"])
def test_airport_stoi_overflow(inp):
    a0 = Airport.search(inp)
    assert not a0.ap.valid
