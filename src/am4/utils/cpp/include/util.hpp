#pragma once
#include <string>
#include <cstdint>
#include <stdexcept>

inline bool str_to_uint16(const std::string& str, uint16_t& out) {
    try {
        std::size_t pos;
        int i = std::stoi(str, &pos);
        if (i < 0 || i > 65535) throw std::out_of_range("out of range");
        if (pos != str.size()) throw std::invalid_argument("trailing");
        out = static_cast<uint16_t>(i);
        return true;
    } catch (std::invalid_argument&) {
    } catch (std::out_of_range&) {
    }
    return false;
}