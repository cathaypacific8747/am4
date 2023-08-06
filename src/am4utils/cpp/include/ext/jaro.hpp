/*
 * adapted from: https://github.com/TriviaMarketing/Jaro-Winkler/tree/master
 * License: MIT
 */

#pragma once
#include <string>

const double JARO_WEIGHT_STRING_A = 1.0 / 3.0;
const double JARO_WEIGHT_STRING_B = 1.0 / 3.0;
const double JARO_WEIGHT_TRANSPOSITIONS = 1.0 / 3.0;

const size_t JARO_WINKLER_PREFIX_SIZE = 4;
const double JARO_WINKLER_SCALING_FACTOR = 0.1;
const double JARO_WINKLER_BOOST_THRESHOLD = 0.7;

#include <algorithm>
#include <vector>

double jaro_distance(const std::string &a, const std::string &b) {
    size_t al = a.size();
    size_t bl = b.size();

    if (al == 0 || bl == 0) return 0.0;

    size_t maxRange = std::max<size_t>(0UL, std::max(al, bl) / 2 - 1);

    std::vector<bool> aMatch(al, false);
    std::vector<bool> bMatch(bl, false);

    // Calculate matching characters.
    size_t matchingCharacters = 0;
    for (size_t ai = 0; ai < al; ++ai) {
        // Calculate window test limits (limit inferior to 0 and superior to bLength).
        size_t minIndex = ai > maxRange ? ai - maxRange : 0;
        size_t maxIndex = std::min(ai + maxRange + 1, bl);

        // No more common character because we don't have characters in b to test
        // with characters in a.
        if (minIndex >= maxIndex) break;
        
        for (size_t bi = minIndex; bi < maxIndex; ++bi) {
            if (!bMatch[bi] && a[ai] == b[bi]) {
                // Found some new match.
                aMatch[ai] = true;
                bMatch[bi] = true;
                ++matchingCharacters;
                break;
            }
        }
    }

    if (matchingCharacters == 0)
        return 0.0;

    // Calculate character transpositions.
    std::vector<size_t> aPosition(matchingCharacters, 0);
    std::vector<size_t> bPosition(matchingCharacters, 0);

    for (size_t ai = 0, pi = 0; ai < al; ++ai) {
        if (aMatch[ai]) {
            aPosition[pi] = ai;
            ++pi;
        }
    }

    for (size_t bi = 0, pi = 0; bi < bl; ++bi) {
        if (bMatch[bi]) {
            bPosition[pi] = bi;
            ++pi;
        }
    }

    // Counting half-transpositions.
    size_t t = 0;
    for (size_t i = 0; i < matchingCharacters; ++i) {
        if (a[aPosition[i]] != b[bPosition[i]]) {
            ++t;
        }
    }

    // Calculate Jaro distance.
    return (
        JARO_WEIGHT_STRING_A * static_cast<double>(matchingCharacters) / static_cast<double>(al) +
        JARO_WEIGHT_STRING_B * static_cast<double>(matchingCharacters) / static_cast<double>(bl) +
        JARO_WEIGHT_TRANSPOSITIONS * (static_cast<double>(matchingCharacters) - static_cast<double>(t) / 2) / static_cast<double>(matchingCharacters)
    );
}

double jaro_winkler_distance(const std::string &a, const std::string &b) {
    double distance = jaro_distance(a, b);

    if (distance > JARO_WINKLER_BOOST_THRESHOLD) {
        // Calculate common string prefix.
        int commonPrefix = 0;
        for (size_t i = 0, indexEnd = std::min(std::min(a.size(), b.size()), JARO_WINKLER_PREFIX_SIZE); i < indexEnd; ++i) {
            if (a[i] == b[i]) {
                ++commonPrefix;
            } else {
                break;
            }
        }

        distance += JARO_WINKLER_SCALING_FACTOR * commonPrefix * (1.0 - distance);
    }

    return distance;
}