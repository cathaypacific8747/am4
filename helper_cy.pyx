#!python
#cython: cdivision=True
cdef int MAX_PLANES_PER_ROUTE = 20

cdef int yTicket_easy(double distance): return <int>(0.44*distance + 185.0)
cdef int jTicket_easy(double distance): return <int>(0.864*distance + 602.8)
cdef int fTicket_easy(double distance): return <int>(1.272*distance + 1270.0)
cdef int yTicket_realism(double distance): return <int>(0.33*distance + 1630.0)
cdef int jTicket_realism(double distance): return <int>(0.648*distance + 538.0)
cdef int fTicket_realism(double distance): return <int>(0.954*distance + 1058.0)

cdef double lTicket_easy(double distance): return <int>(0.0948283724581252 * distance + 85.2045432642377) / 100.0
cdef double hTicket_easy(double distance): return <int>(0.0689663577640275 * distance + 28.2981124272893) / 100.0
cdef double lTicket_realism(double distance): return <int>(0.0776321822039374 * distance + 85.0567600367807000) / 100.0
cdef double hTicket_realism(double distance): return <int>(0.0517742799409248 * distance + 24.6369915396414000) / 100.0

cdef double estLoad(int capacity, double reputation): return <double>capacity * 0.00908971604324 * reputation

cdef int customMin(int a, double b): return a if a < b else <int>b

cdef struct paxConf:
    int yConf
    int jConf
    int fConf
    double maxIncome
    int planesPerRoute
    int yP
    int jP
    int fP
#
cdef struct cargoConf:
    double lPct
    double hPct
    double maxIncome
    int planesPerRoute
    double lP
    double hP
#
cdef double simulatePaxIncome(int y, int j, int f, double yP, double jP, double fP, double yDaily, double jDaily, double fDaily, double distance, double reputation, int flightsPerDay, bint isRealism):
    # example: simulatePaxIncome(600, 0, 0, 10000, 0, 0, 1200, 0, 0, 10000, 100, 2, False)
    cdef double dailyIncome = 0
    cdef double yActual, jActual, fActual
    cdef int flights
    for flights in range(flightsPerDay):
        # estimate the actual load of the aircraft
        # and if the demand is less than the configuration, THAT will be used instead.
        # and subtract that from the daily demand
        
        # potential speedup for removing type conversion?
        yActual = estLoad(customMin(y, yDaily), reputation)
        jActual = estLoad(customMin(j, jDaily), reputation)
        fActual = estLoad(customMin(f, fDaily), reputation)

        yDaily -= yActual
        jDaily -= jActual
        fDaily -= fActual

        # and for whatever the amount of pax carried, add that to the dailyIncome
        dailyIncome += yActual*yP + jActual*jP + fActual*fP
    return dailyIncome

#
cdef double simulateCargoIncome(int l, int h, double lP, double hP, double lDaily, double hDaily, double distance, double reputation, int flightsPerDay, bint isRealism):
    # example: simulateCargoIncome(100000, 0, 1, 0, 200000, 0, 10000, 100, 2, False)
    cdef double dailyIncome = 0
    cdef double lActual, hActual
    cdef int flights
    for flights in range(flightsPerDay):
        lActual = estLoad(customMin(l, lDaily), reputation)
        hActual = estLoad(customMin(h, hDaily), reputation)

        lDaily -= lActual
        hDaily -= hActual

        dailyIncome += lActual*lP + hActual*hP
    return dailyIncome
#
cdef paxConf brutePaxConf(int yD, int jD, int fD, int maxSeats, int flightsPerDay, double distance, double reputation, bint isRealism):
    # example: brutePaxConf(1000, 500, 300, 600, 2, 10000, 100, False)
    cdef paxConf conf
    cdef int y = 0, j = 0, f
    if isRealism:
        conf.yP = yTicket_realism(distance)
        conf.jP = jTicket_realism(distance)
        conf.fP = fTicket_realism(distance)
    else:
        conf.yP = yTicket_easy(distance)
        conf.jP = jTicket_easy(distance)
        conf.fP = fTicket_easy(distance)

    cdef int p = 1
    cdef double incomePerPlanePerDay
    cdef double maxIncome = 0

    cdef int jMax
    for y in reversed(range(maxSeats+1)):
        jMax = (maxSeats - y) / 2
        for j in reversed(range(jMax+1)):
            f = (maxSeats - y - j*2) / 3
            for p in reversed(range(1, MAX_PLANES_PER_ROUTE+1)): # prioritises with more planes/route
                # simulate the depletion of demand per day, starting off with the initial daily demand
                incomePerPlanePerDay = simulatePaxIncome(y*p, j*p, f*p, conf.yP, conf.jP, conf.fP, <double>yD, <double>jD, <double>fD, distance, reputation, flightsPerDay, isRealism) / p 
                if incomePerPlanePerDay > maxIncome:
                    maxIncome = incomePerPlanePerDay
                    conf.yConf = y
                    conf.jConf = j
                    conf.fConf = f
                    conf.planesPerRoute = p
    conf.maxIncome = maxIncome
    return conf
#
cdef cargoConf bruteCargoConf(int lD, int hD, int capacity, double lMultiplier, double hMultiplier, int flightsPerDay, double distance, double reputation, bint isRealism):
    # example: bruteCargoConf(100000, 0, 50000, 1.00, 1.00, 2, 10000, 100, False)
    cdef cargoConf conf
    cdef double lTmp = <double>capacity * lMultiplier * 0.7 / 100
    cdef double hTmp = <double>capacity * hMultiplier / 100

    cdef int lCap = 0
    cdef int hCap = 0

    if isRealism:
        conf.lP = lTicket_realism(distance)
        conf.hP = hTicket_realism(distance)
    else:
        conf.lP = lTicket_easy(distance)
        conf.hP = hTicket_easy(distance)
    
    cdef int p = 1
    cdef double incomePerPlanePerDay
    cdef double maxIncome = 0

    cdef int hPct = 0
    for hPct in range(101):
        lCap = <int>(lTmp * (100 - hPct))
        hCap = <int>(hTmp * hPct)

        for p in reversed(range(1, MAX_PLANES_PER_ROUTE+1)):
            incomePerPlanePerDay = simulateCargoIncome(lCap*p, hCap*p, conf.lP, conf.hP, <double>lD, <double>hD, distance, reputation, flightsPerDay, isRealism) / p
            if incomePerPlanePerDay > maxIncome:
                maxIncome = incomePerPlanePerDay
                conf.lPct = (100-hPct) / 100.0
                conf.hPct = hPct / 100.0
                conf.planesPerRoute = p

    conf.maxIncome = maxIncome
    return conf
#
# sudo yum install python3-devel mysql-devel
# pip3 install mysqlclient
import MySQLdb
def test():
    db = MySQLdb.connect(host='***REMOVED***', user='admin', passwd='***REMOVED***')
    cur = db.cursor()
    cur.execute("select * from am4tools.airports")
    res = cur.fetchall()
    for row in res:
        print(row)
    db.close()

test()