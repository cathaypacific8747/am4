#!python
# cython: cdivision=True
# cython: boundscheck=False
# cython: wraparound=False
# cython: c_string_type=unicode, c_string_encoding=utf8
from cymem.cymem cimport Pool
from libc.math cimport *
cdef extern from "string.h":
    int strcmp(char* str1, char* str2)
import MySQLdb
cdef int MAX_PLANES_PER_ROUTE = 20

# db = MySQLdb.connect(host='localhost', user='root', passwd='***REMOVED***')
db = MySQLdb.connect(host='***REMOVED***', user='admin', passwd='***REMOVED***')
cur = db.cursor()
cur.execute("SELECT id, city, country, iata, icao, runway, market, lat, lng FROM am4tools_api.airports") # query all airports
cdef tuple res = cur.fetchall()

# parse the tuple of tuples into an array of ap_det* structs.
# querying nonexistent airports will lead to SEGFAULT.
cdef:
    struct ap_det:
        bint valid
        char* city
        char* country
        char* iata
        char* icao
        int runway
        int market
        double latRad
        double lonRad
    Pool mem = Pool()
    ap_det* airports = <ap_det*>mem.alloc(3983, sizeof(ap_det))
    list valid_airportIds = []
    int index
    tuple row

for index in range(3983):
    airports[index].valid = False
for row in res:
    index = <int>row[0]
    airports[index].valid = True
    airports[index].city = row[1]
    airports[index].country = row[2]
    airports[index].iata = row[3]
    airports[index].icao = row[4]
    airports[index].runway = <int>row[5]
    airports[index].market = <int>row[6]
    airports[index].latRad = <double>row[7]
    airports[index].lonRad = <double>row[8]

#                       #
# END OF INITIALISATION #
#                       #
cdef int yTicket_easy(double distance): return <int>(1.1*(0.4*distance + 170))-2
cdef int jTicket_easy(double distance): return <int>(1.08*(0.8*distance + 560))-2
cdef int fTicket_easy(double distance): return <int>(1.06*(1.2*distance + 1200))-2
cdef int yTicket_realism(double distance): return <int>(1.1*(0.3*distance + 150))-2
cdef int jTicket_realism(double distance): return <int>(1.08*(0.6*distance + 500))-2
cdef int fTicket_realism(double distance): return <int>(1.06*(0.9*distance + 1000))-2

cdef double lTicket_easy(double distance): return <int>(0.0948283724581252 * distance + 85.2045432642377) / 100.0
cdef double hTicket_easy(double distance): return <int>(0.0689663577640275 * distance + 28.2981124272893) / 100.0
cdef double lTicket_realism(double distance): return <int>(0.0776321822039374 * distance + 85.0567600367807000) / 100.0
cdef double hTicket_realism(double distance): return <int>(0.0517742799409248 * distance + 24.6369915396414000) / 100.0

# cdef double estLoad(double capacity, double reputation): return capacity * 0.00908971604324 * reputation
# cdef double estLoadJ(double capacity, double reputation): return capacity * abs(0.0103323568137 * reputation - 0.116349995389)
cdef double estLoadY(double capacity, double reputation): return capacity * 0.00833436416185 * reputation + 0.0592410115607
cdef double estLoadJ(double capacity, double reputation): return capacity * 0.00833436416185 * reputation + 0.0592410115607
cdef double estLoadF(double capacity, double reputation): return capacity * 0.00844570246176 * reputation + 0.0611838672599
cdef double customMin(int a, double b): return <double>a if a < b else b
cdef double distance(double lat1, double lon1, double lat2, double lon2): return 12742 * asin(sqrt(pow(sin((lat2-lat1) / 2.0), 2) + cos(lat1) * cos(lat2) * pow(sin((lon2-lon1) / 2.0), 2)))


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
cdef double simulatePaxIncome(int y, int j, int f, double yP, double jP, double fP, double yDaily, double jDaily, double fDaily, double distance, double reputation, bint useEstimation):
    cdef double income = 0
    cdef double yActual, jActual, fActual
    if useEstimation:
        yActual = estLoadY(customMin(y, yDaily), reputation)
        jActual = estLoadJ(customMin(j, jDaily), reputation)
        fActual = estLoadF(customMin(f, fDaily), reputation)
    else:
        yActual = customMin(y, yDaily)
        jActual = customMin(j, jDaily)
        fActual = customMin(f, fDaily)
    income += yActual*yP + jActual*jP + fActual*fP
    return income
#
cdef double simulateDailyPaxIncome(int y, int j, int f, double yP, double jP, double fP, double yDaily, double jDaily, double fDaily, double distance, double reputation, int flightsPerDay, bint useEstimation):
    # example: simulateDailyPaxIncome(600, 0, 0, 10000, 0, 0, 1200, 0, 0, 10000, 100, 2)
    cdef double dailyIncome = 0
    cdef double yActual, jActual, fActual
    cdef int flights
    # estimate the actual load of the aircraft (if specified)
    # and if the demand is less than the configuration, THAT will be used instead.
    # and subtract that from the daily demand
    # and for whatever the amount of pax carried, add that to the dailyIncome
    if useEstimation:
        for flights in range(flightsPerDay):
            yActual = estLoadY(customMin(y, yDaily), reputation)
            jActual = estLoadJ(customMin(j, jDaily), reputation)
            fActual = estLoadF(customMin(f, fDaily), reputation)

            yDaily -= yActual
            jDaily -= jActual
            fDaily -= fActual

            dailyIncome += yActual*yP + jActual*jP + fActual*fP
    else:
        for flights in range(flightsPerDay):
            yActual = customMin(y, yDaily)
            jActual = customMin(j, jDaily)
            fActual = customMin(f, fDaily)

            yDaily -= yActual
            jDaily -= jActual
            fDaily -= fActual

            dailyIncome += yActual*yP + jActual*jP + fActual*fP

    return dailyIncome

#
cdef double simulateCargoIncome(int l, int h, double lP, double hP, double lDaily, double hDaily, double distance, double reputation, bint useEstimation):
    cdef double income = 0
    cdef double lActual, hActual
    if useEstimation:
        lActual = estLoadY(customMin(l, lDaily), reputation)
        hActual = estLoadJ(customMin(h, hDaily), reputation)
    else:
        lActual = customMin(l, lDaily)
        hActual = customMin(h, hDaily)
    income += lActual*lP + hActual*hP
    return income
#
cdef double simulateDailyCargoIncome(int l, int h, double lP, double hP, double lDaily, double hDaily, double distance, double reputation, int flightsPerDay, bint useEstimation):
    # example: simulateDailyCargoIncome(100000, 0, 1, 0, 200000, 0, 10000, 100, 2)
    cdef double dailyIncome = 0
    cdef double lActual, hActual
    cdef int flights
    if useEstimation:
        for flights in range(flightsPerDay):
            lActual = estLoadY(customMin(l, lDaily), reputation)
            hActual = estLoadJ(customMin(h, hDaily), reputation)

            lDaily -= lActual
            hDaily -= hActual

            dailyIncome += lActual*lP + hActual*hP
    else:
        for flights in range(flightsPerDay):
            lActual = customMin(l, lDaily)
            hActual = customMin(h, hDaily)

            lDaily -= lActual
            hDaily -= hActual

            dailyIncome += lActual*lP + hActual*hP
    return dailyIncome
#
cdef paxConf brutePaxConf(int yD, int jD, int fD, int maxSeats, int flightsPerDay, double distance, double reputation, bint isRealism, bint useEstimation):
    # example: brutePaxConf(1000, 500, 300, 600, 2, 10000, 100, False, True)
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
    cdef int counter
    for y in reversed(range(maxSeats+1)):
        jMax = (maxSeats - y) / 2
        for j in reversed(range(jMax+1)):
            f = (maxSeats - y - j*2) / 3
            for p in reversed(range(1, MAX_PLANES_PER_ROUTE+1)): # prioritises with more planes/route
                # simulate the depletion of demand per day, starting off with the initial daily demand
                incomePerPlanePerDay = simulateDailyPaxIncome(y*p, j*p, f*p, conf.yP, conf.jP, conf.fP, <double>yD, <double>jD, <double>fD, distance, reputation, flightsPerDay, useEstimation) / <double>p # avoid integer division
                if incomePerPlanePerDay > maxIncome:
                    maxIncome = incomePerPlanePerDay
                    conf.yConf = y
                    conf.jConf = j
                    conf.fConf = f
                    conf.planesPerRoute = p
    conf.maxIncome = maxIncome
    return conf
#
cdef cargoConf bruteCargoConf(int lD, int hD, int capacity, double lMultiplier, double hMultiplier, int flightsPerDay, double distance, double reputation, bint isRealism, bint useEstimation):
    # example: bruteCargoConf(100000, 0, 50000, 1.00, 1.00, 2, 10000, 100, False, True)
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
            incomePerPlanePerDay = simulateDailyCargoIncome(lCap*p, hCap*p, conf.lP, conf.hP, <double>lD, <double>hD, distance, reputation, flightsPerDay, useEstimation) / p
            if incomePerPlanePerDay > maxIncome:
                maxIncome = incomePerPlanePerDay
                conf.lPct = (100-hPct) / 100.0
                conf.hPct = hPct / 100.0
                conf.planesPerRoute = p

    conf.maxIncome = maxIncome
    return conf


#
# this assumes all strings supplied are SQL-injection proof, and already checked for bounds.
cdef struct us_det:
    int discordId
    int gameId
    char* ign
    #
    char* mode
    char* paxMode
    char* cargoMode
    int lTraining
    int hTraining
    int fuelPrice
    int co2Price
    int fuelTraining
    int co2Training
    int useEstimation
    int reputation
cdef class UserSettings:
    cdef public int internalId
    cdef public us_det details
    def __cinit__(self, long discordId=0, int gameId=0, char* ign=''): # supply ONE identifier/argument only!
        cdef bint found = False
        cdef tuple user
        # check if record exists for the specified arguments, if so, store it into self.internalId
        # priority: discordId ($user, $fleet)
        #           gameId (only on $user <some id>, $fleet <some id>)
        #           ign (only on $user <some ign>, $fleet <some ign>, $login)
        # if found, it returns the internalId directly, else, it adds an empty row int the DB and get its internalId, for further use.
        if discordId != 0:
            cur.execute(f"SELECT id FROM am4bot.users WHERE discord_id={discordId}")
            user = cur.fetchone()
            if user != None:
                found = True
                self.internalId = user[0]
        if gameId != 0 and not found:
            cur.execute(f"SELECT id FROM am4bot.users WHERE game_id={gameId}")
            user = cur.fetchone()
            if user != None:
                found = True
                self.internalId = user[0]
        if ign != '' and not found:
            cur.execute(f"SELECT id FROM am4bot.users WHERE ign='{ign}'")
            user = cur.fetchone()
            if user != None:
                found = True
                self.internalId = user[0]

        # internal id does not exist, generate a new row.
        if not found:
            cur.execute(f"INSERT INTO am4bot.users() VALUES()")
            db.commit()
            cur.execute(f"SELECT LAST_INSERT_ID()")
            self.internalId = cur.fetchone()[0]
            if discordId != 0:
                self.update_discordId(discordId)
            if gameId != 0:
                self.update_gameId(gameId)
            if ign != '':
                self.update_ign(ign)

    # functions are split up intentionally to avoid parsing overhead, affecting performance.
    # set
    cpdef void update_discordId(self, long discordId):
        cur.execute(f"UPDATE am4bot.users SET discord_id={discordId} WHERE id={self.internalId}")
        db.commit()

    cpdef void update_gameId(self, int gameId):
        cur.execute(f"UPDATE am4bot.users SET game_id={gameId} WHERE id={self.internalId}")
        db.commit()

    cpdef void update_ign(self, char* ign):
        cur.execute(f"UPDATE am4bot.users SET ign='{ign}' WHERE id={self.internalId}")
        db.commit()
    # set
    cpdef void update_mode(self, char* mode): # 'e', 'r', 'unknown'
        cur.execute(f"UPDATE am4bot.users SET mode='{mode}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_paxMode(self, char* paxMode): # 'y', 'f', 'brute'
        cur.execute(f"UPDATE am4bot.users SET pax_mode='{paxMode}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_cargoMode(self, char* cargoMode): # 'l', 'brute'
        cur.execute(f"UPDATE am4bot.users SET cargo_mode='{cargoMode}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_lTraining(self, int lTraining): # 0-6
        cur.execute(f"UPDATE am4bot.users SET large_training='{lTraining}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_hTraining(self, int hTraining): # 0-6
        cur.execute(f"UPDATE am4bot.users SET heavy_training='{hTraining}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_fuelPrice(self, int fuelPrice): # 0-3000
        cur.execute(f"UPDATE am4bot.users SET fuel_price='{fuelPrice}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_co2Price(self, int co2Price): # 0-200
        cur.execute(f"UPDATE am4bot.users SET co2_price='{co2Price}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_fuelTraining(self, int fuelTraining): # 0-3
        cur.execute(f"UPDATE am4bot.users SET fuel_training='{fuelTraining}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_co2Training(self, int co2Training): # 0-5
        cur.execute(f"UPDATE am4bot.users SET co2_training='{co2Training}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_useEstimation(self, int useEstimation): # 0/1
        cur.execute(f"UPDATE am4bot.users SET use_estimation='{useEstimation}' WHERE id={self.internalId}")
        db.commit()

    cpdef void update_reputation(self, int reputation): # 0-100
        cur.execute(f"UPDATE am4bot.users SET reputation='{reputation}' WHERE id={self.internalId}")
        db.commit()
    # get
    cpdef void getDetails(self):
        cdef tuple user
        cur.execute(f"SELECT discord_id, game_id, ign, mode, pax_mode, cargo_mode, large_training, heavy_training, fuel_price, co2_price, fuel_training, co2_training, use_estimation, reputation FROM am4bot.users WHERE id={self.internalId}")
        user = cur.fetchone()
        
        cdef us_det det
        det.discordId = user[0] if user[0] != None else 0
        det.gameId = user[1] if user[1] != None else 0
        det.ign = user[2] if user[2] != None else ''
        #
        det.mode = user[3]
        det.paxMode = user[4]
        det.cargoMode = user[5]
        det.lTraining = user[6]
        det.hTraining = user[7]
        det.fuelPrice = user[8]
        det.co2Price = user[9]
        det.fuelTraining = user[10] 
        det.co2Training = user[11] 
        det.useEstimation = user[12] 
        det.reputation = user[13]

        self.details = det
    # demo
    '''
    x = UserSettings(gameId=54557)
    x.update_mode('r')
    x.update_paxMode('f')
    x.update_cargoMode('l')
    x.update_lTraining(6)
    x.update_hTraining(6)
    x.update_fuelPrice(1000)
    x.update_co2Price(150)
    x.update_fuelTraining(3)
    x.update_co2Training(5)
    x.update_useEstimation(0)
    x.update_reputation(55)
    x.getSettings()
    print(x.details)
    '''
    

#
cdef struct gs_det:
    long guildId
    char* prefix
    long easyRoleId
    long realismRoleId
cdef class GuildSettings:
    cdef public int internalId
    cdef public gs_det details
    #
    def __cinit__(self, long guildId): # guildId is REQUIRED.
        cdef tuple guild
        # check if record exists, if not, create a new entry for it, and store it as an internal id.
        cur.execute(f"SELECT id FROM am4bot.guilds WHERE guild_id={guildId}")
        guild = cur.fetchone()
        if guild != None: # found
            self.internalId = guild[0]
        else:
            cur.execute(f"INSERT INTO am4bot.guilds(guild_id) VALUES({guildId})")
            db.commit()
            cur.execute(f"SELECT LAST_INSERT_ID()")
            self.internalId = cur.fetchone()[0]
    # set
    cpdef void update_prefix(self, char* prefix): # '$'
        cur.execute(f"UPDATE am4bot.guilds SET prefix='{prefix}' WHERE id={self.internalId}")
        db.commit()
    cpdef void update_easyRoleId(self, long easyRoleId):
        cur.execute(f"UPDATE am4bot.guilds SET easy_role_id='{easyRoleId}' WHERE id={self.internalId}")
        db.commit()
    cpdef void update_realismRoleId(self, long realismRoleId):
        cur.execute(f"UPDATE am4bot.guilds SET realism_role_id='{realismRoleId}' WHERE id={self.internalId}")
        db.commit()
    # get
    cpdef void getDetails(self):
        cdef tuple guild
        cur.execute(f"SELECT guild_id, prefix, easy_role_id, realism_role_id FROM am4bot.guilds WHERE id={self.internalId}")
        guild = cur.fetchone()
        
        cdef gs_det det
        det.guildId = guild[0]
        det.prefix = guild[1] if guild[1] != None else ''
        det.easyRoleId = guild[2] if guild[2] != None else 0
        det.realismRoleId = guild[3] if guild[3] != None else 0

        self.details = det
    # demo
    '''
    x = GuildSettings(473892865081081856)
    x.update_prefix('.')
    x.update_easyRoleId(474359813980291073)
    x.update_realismRoleId(474359896066752512)
    x.getSettings()
    print(x.details)
    '''
#
cdef class Airport:
    cdef public bint success
    cdef public int internalId
    cdef public ap_det details

    def __cinit__(self, int apid=0, char* text=''):
        cdef tuple idresult
        self.success = False

        if apid != 0:
            if airports[apid].valid:
                self.internalId = apid
                self.success = True
        elif text != '':
            cur.execute(f"SELECT id FROM am4tools_api.airports WHERE iata='{text}' OR icao='{text}' OR id='{text}'")
            idresult = cur.fetchone()
            if idresult != None:
                self.internalId = idresult[0]
                self.success = True
        
        if self.success:
            self.details = airports[self.internalId]
    
    # demo
    '''
    a = Airport(text='LHR')
    print(a.details)
    '''
#
cdef struct stpvr_det:
    bint success
    int apid
    double flyingDistance
    double diff
cdef class Route: # assumes that input airports exists already
    cdef public Airport origin
    cdef public Airport destination
    cdef public double distance
    cdef public stpvr_det stopover
    #
    def __cinit__(self, Airport orig, Airport dest):
        self.origin = orig
        self.destination = dest
        self.distance = distance(self.origin.details.latRad, self.origin.details.lonRad, self.destination.details.latRad, self.destination.details.lonRad)
    #
    cpdef void findStopover(self, int maxRange, int rwyReq):
        cdef double toO = 0
        cdef double toD = 0

        cdef double origLat = self.origin.details.latRad
        cdef double origLon = self.origin.details.lonRad
        cdef double thisLat
        cdef double thisLon
        cdef double destLat = self.destination.details.latRad
        cdef double destLon = self.destination.details.lonRad

        cdef double lowestSum = 32768
        cdef int k_last = 0

        cdef int k
        for k in range(1, 3983):
            if airports[k].runway < rwyReq:
                continue
            thisLat = airports[k].latRad
            thisLon = airports[k].lonRad
            toO = distance(origLat, origLon, thisLat, thisLon)
            if toO > maxRange or toO < 100:
                continue
            toD = distance(thisLat, thisLon, destLat, destLon)
            if toD > maxRange or toD < 100:
                continue

            if toO + toD < lowestSum:
                lowestSum = toO + toD
                k_last = k
        #
        if k_last == 0: # if the old 0 was not overwritten, then there are no suitable stopovers
            self.stopover.success = False
        else:
            self.stopover.success = True
            self.stopover.apid = k_last
            self.stopover.flyingDistance = lowestSum
            self.stopover.diff = lowestSum - self.distance
    # demo
    '''
    r = Route(Airport(text='LHR'), Airport(text='SYD'))
    print(r.distance)

    r.findStopover(maxRange=14500, rwyReq=0)
    print(r.stopover)
    '''
#
r = Route(Airport(text='LHR'), Airport(text='SYD'))
r.findStopover(maxRange=14500, rwyReq=0)
print(r.__dict__)

db.close()
print('Connection closed.')