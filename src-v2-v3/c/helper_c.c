#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <stdlib.h>

// for mmap
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/io.h>
#include <sys/mman.h>
#include <string.h>

#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX_PLANES_PER_ROUTE 20

struct paxConf {
    int yConf;
    int jConf;
    int fConf;
    double maxIncome;
    int planesPerRoute;
    double yP;
    double jP;
    double fP;
};

struct cargoConf {
    double lPct;
    double hPct;
    double maxIncome;
    int planesPerRoute;
    double lP;
    double hP;
};

struct airportEntry {
    char city[37];
    char region[33];
    char iata[5];
    char icao[5];
    int runway;
    int market;
    double latRad;
    double lonRad;
};

struct demandEntry {
    int yDemand;
    int jDemand;
    int fDemand;
    double distance;
};

struct stopoverEntry {
    int apId;
    double toO;
    double toD;
};


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

double simulatePaxIncome(int y, int j, int f, double yP, double jP, double fP, double yDaily, double jDaily, double fDaily, double distance, double reputation, int flightsPerDay, bool isRealism) {
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
        dailyIncome += yActual * yP + jActual * jP + fActual * fP;
    }
    return dailyIncome;
}

double simulateCargoIncome(int l, int h, double lP, double hP, double lDaily, double hDaily, double distance, double reputation, int flightsPerDay, bool isRealism) {
    int dailyIncome = 0;
    double lActual, hActual;
    for (int flights = 0; flights < flightsPerDay; flights++) {
        lActual = estLoad(MIN(l, lDaily), reputation);
        hActual = estLoad(MIN(h, hDaily), reputation);

        lDaily -= lActual;
        hDaily -= hActual;

        dailyIncome += lActual * lP + hActual * hP;
    }
    return dailyIncome;
}

// O(n²)
// change to malloc()!
struct paxConf brutePaxConf(int yD, int jD, int fD, int maxSeats, int flightsPerDay, double distance, double reputation, bool isRealism) {
    static struct paxConf conf; // change to malloc pls
    int y = 0, j = 0, f;
    if (isRealism) {
        conf.yP = yTicket_realism(distance);
        conf.jP = jTicket_realism(distance);
        conf.fP = fTicket_realism(distance);
    } else {
        conf.yP = yTicket_easy(distance);
        conf.jP = jTicket_easy(distance);
        conf.fP = fTicket_easy(distance);
    }

    int p;
    double incomePerPlanePerDay;
    double maxIncome = 0;

    int jMax;
    for (y = maxSeats; y >= 0; y--) {
        jMax = (maxSeats - y) / 2;
        for (j = jMax; j >= 0; j--) {
            f = (maxSeats - y - j*2) / 3;

            for (p = MAX_PLANES_PER_ROUTE; p > 0; p--) { // prioritize more planes per route
                // simulate the depletion of demand per day, starting off with the initial daily demand
                incomePerPlanePerDay = simulatePaxIncome(y*p, j*p, f*p, conf.yP, conf.jP, conf.fP, (double)yD, (double)jD, (double)fD, distance, reputation, flightsPerDay, isRealism) / p;
                
                if (incomePerPlanePerDay > maxIncome) {
                    maxIncome = incomePerPlanePerDay;
                    conf.yConf = y;
                    conf.jConf = j;
                    conf.fConf = f;
                    conf.planesPerRoute = p;
                }
            }
        }
    }
    conf.maxIncome = maxIncome;
    return conf;
}

// change to malloc()!
struct cargoConf bruteCargoConf(int lD, int hD, int capacity, double lMultiplier, double hMultiplier, int flightsPerDay, double distance, double reputation, bool isRealism) {
    static struct cargoConf conf;
    double lCap = 0;
    double hCap = 0;

    if (isRealism) {
        conf.lP = lTicket_realism(distance);
        conf.hP = hTicket_realism(distance);
    } else {
        conf.lP = lTicket_easy(distance);
        conf.hP = hTicket_easy(distance);
    }

    int p;

    double incomePerPlanePerDay;
    double maxIncome = 0;

    double hPct;
    for (hPct = 0; hPct < 1.01; hPct += 0.01) {
        lCap = (double)capacity * 0.7 * lMultiplier * (1.00 - hPct);
        hCap = (double)capacity * hMultiplier * hPct;

        for (p = MAX_PLANES_PER_ROUTE; p > 0; p--) {
            incomePerPlanePerDay = simulateCargoIncome(lCap*p, hCap*p, conf.lP, conf.hP, (double)lD, (double)hD, distance, reputation, flightsPerDay, isRealism) / p;

            if (incomePerPlanePerDay > maxIncome) {
                maxIncome = incomePerPlanePerDay;
                conf.lPct = 1.00-hPct;
                conf.hPct = hPct;
                conf.planesPerRoute = p;
            }
        }
    }
    conf.maxIncome = maxIncome;
    return conf;
}

// remember to free str!
char* readFile(char* filename) {
    // not intended ot be exposed to Python.
    int fd = open(filename, O_RDONLY);
    struct stat s;
    if (fstat(fd, &s) == -1)
        return NULL;

    int fileSize = s.st_size;
    char *f = mmap(NULL, fileSize, PROT_READ, MAP_PRIVATE, fd, 0);
    char *str = malloc(sizeof(char)*fileSize + 1);
    strcpy(str, f);

    return str;
}

struct airportEntry airports[3983]; // airports[x].city == "INVALID" means it does not exist.
bool initAirports() {
    char *str = readFile("data/ap-indexed-radians.csv");
    if (str == NULL)
        return false; // unable to malloc() or read file
    
    char *strStart = str;
    for (int temp; str != NULL; ) {
        temp = atoi(strsep(&str, ";")); 
        if (temp == 0) {
            strsep(&str, "\n");
            continue;
        }
        strcpy(airports[temp].city, strsep(&str, ";"));   // max = 36
        strcpy(airports[temp].region, strsep(&str, ";")); // max = 32
        strcpy(airports[temp].iata, strsep(&str, ";"));   // max = 4 (EGMD, TIST)
        strcpy(airports[temp].icao, strsep(&str, ";"));   // max = 4
        airports[temp].runway = atoi(strsep(&str, ";"));
        airports[temp].market = atoi(strsep(&str, ";"));
        airports[temp].latRad = atof(strsep(&str, ";"));
        airports[temp].lonRad = atof(strsep(&str, "\n"));
    }
    free(strStart);
    return true;
}

// remember to free demand!
struct demandEntry *queryDemands(int airportId) {
    // not intended ot be exposed to Python.
    struct demandEntry *demand = malloc(sizeof(struct demandEntry)*3983);
    
    char fileName[19];
    sprintf(fileName, "data/dist/%d.csv", airportId);
    char *str = readFile(fileName);
    if (str == NULL)
        return demand;
    
    char *strStart = str;
    for (int i; str != NULL;) {
        i = atoi(strsep(&str, ","));
        demand[i].yDemand = atoi(strsep(&str, ","));
        demand[i].jDemand = atoi(strsep(&str, ","));
        demand[i].fDemand = atoi(strsep(&str, ","));
        demand[i].distance = atof(strsep(&str, "\n"));
    }
    free(strStart);
    // printf("%d\n", demand[2].yDemand);
    return demand;
    // free(demand);
}

void paxRoutes(int airportId, int capacity, double distance, int flightsPerDay, double reputation, bool isRealism) {
    struct demandEntry *demand = queryDemands(airportId);
    for (int k = 1; k < 3983; k++) {
        if(demand[k].yDemand > 0 && demand[k].distance < distance) {
            printf("%d/%d/%d\n", demand[k].yDemand, demand[k].jDemand, demand[k].fDemand);
            // valid.
        }
    }
    free(demand);
}

double distance(double lat1, double lon1, double lat2, double lon2) { // in radians
    return 12742 * asin(sqrt(pow(sin((lat2-lat1) / (double)2), 2) + cos(lat1) * cos(lat2) * pow(sin((lon2-lon1) / (double)2), 2)));
}

// remember to free 'result'!
struct stopoverEntry *stopover(int origId, int destId, int range, int rwyReq) {
    double toO = 0;
    double toD = 0;

    double origLat = airports[origId].latRad;
    double origLon = airports[origId].lonRad;
    double thisLat;
    double thisLon;
    double destLat = airports[destId].latRad;
    double destLon = airports[destId].lonRad;

    double thisLowestSum = 0;
    double lowestSum = 65536;
    int apId = 0;
    struct stopoverEntry *result = malloc(sizeof(struct stopoverEntry));

    for (int k = 1; k < 3983; k++) {
        if (airports[k].runway < rwyReq)
            continue;

        thisLat = airports[k].latRad;
        thisLon = airports[k].lonRad;
        toO = distance(origLat, origLon, thisLat, thisLon);
        if ((toO > range) || (toO < 100))
            continue;
        toD = distance(thisLat, thisLon, destLat, destLon);
        if ((toD > range) || (toD < 100))
            continue;

        thisLowestSum = toO + toD;
        if (thisLowestSum < lowestSum) {
            lowestSum = thisLowestSum;
            apId = k;
        }
    }

    result->apId = apId;
    result->toO = toO;
    result->toD = toD;
    return result;
}

double calcFuel(double consumption, int distance, double trainingMultiplier, double modificationMultiplier) {
    return consumption*distance*trainingMultiplier*modificationMultiplier;
    // trainingMultiplier: 1.00, 0.99, 0.98, 0.97
    // modificationMultiplier: 1.00, 0.90
}

double calcPaxCO2(double consumption, double distance, int yActual, int jActual, int fActual, int yCapacity, int jCapacity, int fCapacity, double trainingMultiplier, double modificationMultiplier) {
    return trainingMultiplier*(ceil(distance)*round(modificationMultiplier*consumption)*(yActual + 2*jActual + 3*fActual) + (yCapacity + jCapacity + fCapacity));
    // trainingMultiplier: 1.00, 0.99, 0.98, 0.97, 0.96, 0.95
    // modificationMultiplier: 1.00, 0.90
}

double calcCargoCO2(double consumption, double distance, int lActual, int hActual, int lCapacity, int hCapacity, double trainingMultiplier, double modificationMultiplier) {
    return trainingMultiplier*(ceil(distance)*round(modificationMultiplier*consumption)*(lActual/(double)1000 + hActual/(double)500) + (lCapacity + hCapacity));
    // trainingMultiplier: 1.00, 0.99, 0.98, 0.97, 0.96, 0.95
    // modificationMultiplier: 1.00, 0.90
}