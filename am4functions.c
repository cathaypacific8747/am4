#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#define MIN(a,b) (((a)<(b))?(a):(b))

// pax ticket prices
int yTicket_easy(double distance) { return (int)(0.44*distance + 185); } // 1.1*(0.4*d+170)-2
int jTicket_easy(double distance) { return (int)(0.864*distance + 602.8); } // 1.08*(0.8*d+560)-2
int fTicket_easy(double distance) { return (int)(1.272*distance + 1270); }// 1.06*(1.2*d+1200)-2
int yTicket_realism(double distance) { return (int)(0.33*distance + 163); } // 1.1*(0.3*d+150)-2
int jTicket_realism(double distance) { return (int)(0.648*distance + 538); } // 1.08*(0.6*d+500)-2
int fTicket_realism(double distance) { return (int)(0.954*distance + 1058); } // 1.06*(0.9*d+1000)-2

// cargo ticket prices
double lTicket_easy(double distance) { return floor(0.0948283724581252 * distance + 85.2045432642377) / 100; }
double hTicket_easy(double distance) { return floor(0.0689663577640275 * distance + 28.2981124272893) / 100; }
double lTicket_realism(double distance) { return floor(0.0776321822039374 * distance + 85.0567600367807000) / 100; }
double hTicket_realism(double distance) { return floor(0.0517742799409248 * distance + 24.6369915396414000) / 100; }

double estLoad(int capacity, double reputation) { return (double)capacity * 0.00908971604324 * reputation; }



double simulatePaxIncome(int y, int j, int f, double yDaily, double jDaily, double fDaily, double distance, double reputation, int flightsPerDay, bool isRealism) {
    int dailyIncome = 0;
    double yActual, jActual, fActual;
    for (int flights = 0; flights < flightsPerDay; flights++) {
        // estiamte the actual load of the aircraft
        // and if the demand is less than the configuration, that will be used instead.
        // and subtract that from the daily demand
        yActual = estLoad(MIN(y, yDaily), reputation);
        jActual = estLoad(MIN(j, jDaily), reputation);
        fActual = estLoad(MIN(f, fDaily), reputation);

        yDaily -= yActual;
        jDaily -= jActual;
        fDaily -= fActual;

        // and for whatever the amount of pax carried, add that to the dailyIncome
        if (isRealism) {
            dailyIncome += yActual * yTicket_realism(distance) + jActual * jTicket_realism(distance) + fActual * fTicket_realism(distance);
        } else {
            dailyIncome += yActual * yTicket_easy(distance) + jActual * jTicket_easy(distance) + fActual * fTicket_easy(distance);
        }
    }
    return dailyIncome;
}

double simulateCargoIncome(int l, int h, double lDaily, double hDaily, double distance, double reputation, int flightsPerDay, bool isRealism) {
    int dailyIncome = 0;
    double lActual, hActual;
    for (int flights = 0; flights < flightsPerDay; flights++) {
        lActual = estLoad(MIN(l, lDaily), reputation);
        hActual = estLoad(MIN(h, hDaily), reputation);

        lDaily -= lActual;
        hDaily -= hActual;

        if (isRealism) {
            dailyIncome += lActual * lTicket_realism(distance) + hActual * hTicket_realism(distance);
        } else {
            dailyIncome += lActual * lTicket_easy(distance) + hActual * hTicket_easy(distance);
        }
    }
    return dailyIncome;
}

int* brutePaxConf(int yD, int jD, int fD, int maxSeats, int flightsPerDay, double distance, double reputation, bool isRealism) {
    int y = 0, j = 0, f;

    static int conf[4];
    double dailyIncome;
    double maxIncome = 0;

    int jMax;
    for (y = maxSeats; y >= 0; y--) {
        jMax = (maxSeats - y) / 2;
        for (j = jMax; j >= 0; j--) {
            f = (maxSeats - y - j*2) / 3;

            // simulate the depletion of demand per day, starting off with the initial daily demand
            dailyIncome = simulatePaxIncome(y, j, f, (double)yD, (double)jD, (double)fD, distance, reputation, flightsPerDay, isRealism);

            if (dailyIncome > maxIncome) {
                maxIncome = dailyIncome;
                conf[0] = y;
                conf[1] = j;
                conf[2] = f;
            }
        }
    }
    conf[3] = (int)maxIncome;
    return conf;
}

int* bruteCargoConf(int lD, int hD, int capacity, double lMultiplier, double hMultiplier, int flightsPerDay, double distance, double reputation, bool isRealism) {
    double lCap = 0;
    double hCap = 0;

    static int conf[3];
    double dailyIncome;
    double maxIncome = 0;

    double hPct;
    for (hPct = 0; hPct < 1.01; hPct += 0.01) {
        lCap = (double)capacity * 0.7 * lMultiplier * (1.00 - hPct);
        hCap = (double)capacity * hMultiplier * hPct;

        dailyIncome = simulateCargoIncome(lCap, hCap, (double)lD, (double)hD, distance, reputation, flightsPerDay, isRealism);

        if (dailyIncome > maxIncome) {
            maxIncome = dailyIncome;
            conf[0] = (int)(100*(1.00-hPct));
            conf[1] = (int)(100*hPct);
        }
    }
    conf[2] = (int)maxIncome;
    return conf;
}



// int main() {
//     int *c = brutePaxConf(200);
//     for (int i = 0; i < 3; i++)
//         printf("%d,", *(c+i));
// }