#pragma once
#include "enums.h"

#include <string>
#include <cstdint>

using std::string;

struct Aircraft {
    uint16_t id;
    string shortname;
    string manufacturer;
    string name;
    AircraftType type;
    uint8_t priority;
    int16_t eid;
    string ename;
    float speed;
    float fuel;
    float co2;
    uint32_t cost;
    uint32_t capacity;
    int16_t rwy;
    uint32_t check_cost;
    int16_t range;
    int16_t ceil;
    int16_t maint;
    uint8_t pilots;
    uint8_t crew;
    uint8_t engineers;
    uint8_t technicians;
    string img;
    uint8_t wingspan;
    uint8_t length;

    bool valid = false;
};