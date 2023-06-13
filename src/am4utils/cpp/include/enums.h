#pragma once

enum GameMode {
    EASY,
    REALISM
};

enum class AirportSearchType {
    ALL,
    IATA,
    ICAO,
    NAME,
    ID,
};

enum AircraftType {
    PAX,
    CARGO,
    VIP
};

enum class AircraftSearchType {
    ALL,
    ID,
    SHORTNAME,
    NAME
};

enum PaxConfigAlgorithm {
    FJY, FYJ,
    JFY, JYF,
    YJF, YFJ,
};