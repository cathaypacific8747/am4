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
    size_t aLength = a.size();
    size_t bLength = b.size();

    if (aLength == 0 || bLength == 0) return 0.0;

    size_t maxRange = std::max(0UL, std::max(aLength, bLength) / 2 - 1);

    std::vector<bool> aMatch(aLength, false);
    std::vector<bool> bMatch(bLength, false);

    // Calculate matching characters.
    size_t matchingCharacters = 0;
    for (size_t aIndex = 0; aIndex < aLength; ++aIndex) {
        // Calculate window test limits (limit inferior to 0 and superior to bLength).
        // size_t minIndex = std::max(aIndex - maxRange, 0UL);
        size_t minIndex = aIndex > maxRange ? aIndex - maxRange : 0;
        size_t maxIndex = std::min(aIndex + maxRange + 1, bLength);

        // No more common character because we don't have characters in b to test
        // with characters in a.
        if (minIndex >= maxIndex) break;
        
        for (size_t bIndex = minIndex; bIndex < maxIndex; ++bIndex) {
            if (!bMatch.at(bIndex) && a.at(aIndex) == b.at(bIndex)) {
                // Found some new match.
                aMatch[aIndex] = true;
                bMatch[bIndex] = true;
                ++matchingCharacters;
                break;
            }
        }
    }

    // If no matching characters, we return 0.
    if (matchingCharacters == 0) {
        return 0.0;
    }

    // Calculate character transpositions.
    std::vector<size_t> aPosition(matchingCharacters, 0);
    std::vector<size_t> bPosition(matchingCharacters, 0);

    for (size_t aIndex = 0, positionIndex = 0; aIndex < aLength; ++aIndex) {
        if (aMatch.at(aIndex)) {
            aPosition[positionIndex] = aIndex;
            ++positionIndex;
        }
    }

    for (size_t bIndex = 0, positionIndex = 0; bIndex < bLength; ++bIndex) {
        if (bMatch.at(bIndex)) {
            bPosition[positionIndex] = bIndex;
            ++positionIndex;
        }
    }

    // Counting half-transpositions.
    size_t transpositions = 0;
    for (size_t i = 0; i < matchingCharacters; ++i) {
        if (a.at(aPosition.at(i)) != b.at(bPosition.at(i))) {
            ++transpositions;
        }
    }

    // Calculate Jaro distance.
    return (
        JARO_WEIGHT_STRING_A * static_cast<double>(matchingCharacters) / static_cast<double>(aLength) +
        JARO_WEIGHT_STRING_B * static_cast<double>(matchingCharacters) / static_cast<double>(bLength) +
        JARO_WEIGHT_TRANSPOSITIONS * (static_cast<double>(matchingCharacters) - static_cast<double>(transpositions) / 2) / static_cast<double>(matchingCharacters)
    );
}

double jaro_winkler_distance(const std::string &a, const std::string &b) {
    double distance = jaro_distance(a, b);

    if (distance > JARO_WINKLER_BOOST_THRESHOLD) {
        // Calculate common string prefix.
        int commonPrefix = 0;
        for (size_t i = 0, indexEnd = std::min(std::min(a.size(), b.size()), JARO_WINKLER_PREFIX_SIZE); i < indexEnd; ++i) {
            if (a.at(i) == b.at(i)) {
                ++commonPrefix;
            } else {
                break;
            }
        }

        distance += JARO_WINKLER_SCALING_FACTOR * commonPrefix * (1.0 - distance);
    }

    return distance;
}