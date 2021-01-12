'''

Requests alliance details specified at 'data/watchlist.csv' on initial code run and every 1 hour, logging it to:
- data/log/allianceLog.json    | keeping data for up to 14 days, prettified.
- data/log/allianceLogWeb.json | keeping data for up to 6 hours, minified.

Automatically switches API keys if requests remaining drops below 25.
WIP: Error handling.

'''

import urllib3
import json
import time
from urllib.parse import quote

tokens = {
    'default': '***REMOVED***',
    'backup1': '***REMOVED***',
}
mode = 'default'

while 1:
    try:
        with open('data/watchlist.csv', 'r', encoding='utf-8') as g:
            watchlist = g.read().split(',')
            http = urllib3.PoolManager()
            for allianceName in watchlist:
                try:
                    thisData = json.loads(http.request('GET', f'https://www.airline4.net/api/?access_token={tokens[mode]}&search={quote(allianceName)}').data.decode('utf-8'))
                    # thisData = {"status":{"request":"success","requests_remaining":7},"alliance":[{"name":"Star Alliance","rank":1,"members":60,"maxMembers":60,"value":115.71,"ipo":1,"minSV":250}],"members":[{"company":"VaioAir","joined":1583915711,"flights":106120,"contributed":5495759,"dailyContribution":52652,"online":1595900790,"shareValue":8757.97},{"company":"Eurolines","joined":1583831999,"flights":67311,"contributed":3821498,"dailyContribution":30007,"online":1595887893,"shareValue":6148.32},{"company":"CallumAir","joined":1583833492,"flights":61307,"contributed":3207887,"dailyContribution":29381,"online":1595880640,"shareValue":3914.05},{"company":"Air land","joined":1583874467,"flights":60838,"contributed":3147669,"dailyContribution":28167,"online":1595876453,"shareValue":4602.61},{"company":"MANGALORE AIRLINES","joined":1583834824,"flights":103274,"contributed":3141067,"dailyContribution":30813,"online":1595904910,"shareValue":3413.57},{"company":"Planet Express","joined":1583914445,"flights":77234,"contributed":3069385,"dailyContribution":33169,"online":1595905242,"shareValue":1787.95},{"company":"Scuderia Airlines","joined":1583832203,"flights":55468,"contributed":2983456,"dailyContribution":26048,"online":1595904373,"shareValue":4716.6},{"company":"Swalife Air","joined":1583842685,"flights":53009,"contributed":2882001,"dailyContribution":29531,"online":1595905244,"shareValue":3731.38},{"company":"JEI Airlines","joined":1583837053,"flights":80893,"contributed":2846567,"dailyContribution":26491,"online":1595882768,"shareValue":1668.05},{"company":"Husaria Poland","joined":1583843175,"flights":54678,"contributed":2820249,"dailyContribution":24281,"online":1595891819,"shareValue":4383.27},{"company":"Penguin Airways.","joined":1583835689,"flights":49572,"contributed":2804597,"dailyContribution":36260,"online":1595886526,"shareValue":3639.59},{"company":"FLYOURAIR","joined":1583843108,"flights":47375,"contributed":2801832,"dailyContribution":31916,"online":1595896862,"shareValue":3296.42},{"company":"Intercontinental Airlines","joined":1583835062,"flights":48729,"contributed":2705820,"dailyContribution":24386,"online":1595905115,"shareValue":1685.75},{"company":"Shakti Airlines","joined":1585732447,"flights":46072,"contributed":2700993,"dailyContribution":33148,"online":1595905029,"shareValue":2833.18},{"company":"AirAsia ","joined":1583934884,"flights":41555,"contributed":2686998,"dailyContribution":32246,"online":1595904642,"shareValue":1571.91},{"company":"turtle","joined":1583835669,"flights":40566,"contributed":2589246,"dailyContribution":36900,"online":1595905219,"shareValue":1307.58},{"company":"Lucas Aerospace","joined":1583836188,"flights":44321,"contributed":2551633,"dailyContribution":21466,"online":1595905241,"shareValue":3251.29},{"company":"FLY 365","joined":1583843313,"flights":44579,"contributed":2542983,"dailyContribution":22355,"online":1595887104,"shareValue":3083.43},{"company":"Hooters air","joined":1583835544,"flights":47092,"contributed":2538347,"dailyContribution":23739,"online":1595901336,"shareValue":2325.28},{"company":"Drug PushAir","joined":1587298617,"flights":61271,"contributed":2503905,"dailyContribution":32795,"online":1595895265,"shareValue":2240.45},{"company":"Lanz Air","joined":1587347299,"flights":56036,"contributed":2419874,"dailyContribution":24926,"online":1595905240,"shareValue":2439.06},{"company":"Mabuhay Airways","joined":1586430502,"flights":32147,"contributed":2369501,"dailyContribution":29737,"online":1595905187,"shareValue":2718.85},{"company":"The Emirates Air","joined":1587347545,"flights":47768,"contributed":2349744,"dailyContribution":26626,"online":1595902929,"shareValue":2725.81},{"company":"Dragoon20005","joined":1583832056,"flights":68121,"contributed":2324505,"dailyContribution":22836,"online":1595904947,"shareValue":692.77},{"company":"LOT","joined":1583914826,"flights":46710,"contributed":2298127,"dailyContribution":21508,"online":1595892172,"shareValue":2835.01},{"company":"Nunas Air","joined":1583874424,"flights":46272,"contributed":2177928,"dailyContribution":22644,"online":1595889976,"shareValue":2482.81},{"company":"Sudo","joined":1583859025,"flights":41784,"contributed":2159958,"dailyContribution":19784,"online":1595872635,"shareValue":2952.69},{"company":"Canton9Air","joined":1583934018,"flights":50221,"contributed":2117548,"dailyContribution":19832,"online":1595891624,"shareValue":1819.18},{"company":"JAGS","joined":1583874585,"flights":40597,"contributed":2114189,"dailyContribution":18979,"online":1595896337,"shareValue":3098.37},{"company":"LUXURAIR","joined":1583835500,"flights":37310,"contributed":1968736,"dailyContribution":23144,"online":1595871942,"shareValue":2208.99},{"company":"Shwarma Air","joined":1588872743,"flights":29801,"contributed":1896234,"dailyContribution":23512,"online":1595868825,"shareValue":2080.2},{"company":"Cathay Express","joined":1583832879,"flights":39284,"contributed":1840203,"dailyContribution":20717,"online":1595904314,"shareValue":2097.02},{"company":"Global Air","joined":1583837861,"flights":33098,"contributed":1713075,"dailyContribution":24196,"online":1595887571,"shareValue":2389.59},{"company":"YHJ airline","joined":1590049322,"flights":34094,"contributed":1685270,"dailyContribution":25116,"online":1595904218,"shareValue":1117.76},{"company":"HeshaMaria Airlines","joined":1591094726,"flights":27849,"contributed":1659466,"dailyContribution":35242,"online":1595883966,"shareValue":2401.93},{"company":"Elegance Airways","joined":1589873278,"flights":26280,"contributed":1607478,"dailyContribution":22553,"online":1595891353,"shareValue":2572.35},{"company":"Blue Moon Airlines","joined":1585604671,"flights":51164,"contributed":1583670,"dailyContribution":27088,"online":1595901716,"shareValue":1051.64},{"company":"Star fleer","joined":1587283599,"flights":32097,"contributed":1523073,"dailyContribution":23585,"online":1595880379,"shareValue":1564.98},{"company":"MAW Airways","joined":1590327408,"flights":26765,"contributed":1486457,"dailyContribution":30893,"online":1595901238,"shareValue":1612.4},{"company":"BW-Fly","joined":1590785552,"flights":22740,"contributed":1467219,"dailyContribution":22550,"online":1595882590,"shareValue":2498.41},{"company":"RG1405","joined":1591608579,"flights":20637,"contributed":1205590,"dailyContribution":27925,"online":1595897207,"shareValue":2885.56},{"company":"Shubh Airways","joined":1591697873,"flights":21297,"contributed":1191215,"dailyContribution":27185,"online":1595902672,"shareValue":1561.96},{"company":"SappAir","joined":1590687386,"flights":25382,"contributed":1184514,"dailyContribution":20307,"online":1595892645,"shareValue":1114.8},{"company":"Sunshine airway","joined":1591431584,"flights":22512,"contributed":1078128,"dailyContribution":23244,"online":1595899974,"shareValue":929.41},{"company":"AURORA_AIR","joined":1592563383,"flights":13659,"contributed":1043968,"dailyContribution":31776,"online":1595905230,"shareValue":1288.31},{"company":"ASIA PACIFIC AIRLINE","joined":1594008961,"flights":9549,"contributed":969956,"dailyContribution":38791,"online":1595903840,"shareValue":355.97},{"company":"Bloody Hunter","joined":1592296206,"flights":13875,"contributed":890611,"dailyContribution":20966,"online":1595875055,"shareValue":2325.35},{"company":"Tesla Airlines","joined":1591418301,"flights":19627,"contributed":879454,"dailyContribution":23740,"online":1595901856,"shareValue":444.47},{"company":"BulldogAir ","joined":1591613035,"flights":14524,"contributed":868798,"dailyContribution":14551,"online":1595882939,"shareValue":1165.13},{"company":"ZEYNEPSU","joined":1593661605,"flights":8832,"contributed":767617,"dailyContribution":31156,"online":1595878382,"shareValue":1386.51},{"company":"Rastan Global","joined":1593661269,"flights":9128,"contributed":754001,"dailyContribution":31195,"online":1595881845,"shareValue":1113.31},{"company":"Canezix","joined":1593664976,"flights":9065,"contributed":731510,"dailyContribution":24160,"online":1595876439,"shareValue":2499.03},{"company":"Motion","joined":1593651612,"flights":6861,"contributed":708461,"dailyContribution":32354,"online":1595897686,"shareValue":1264.02},{"company":"FLY INDIAN AIRWAYS","joined":1593693041,"flights":12915,"contributed":675658,"dailyContribution":31519,"online":1595904705,"shareValue":684.98},{"company":"Caniços Air Line","joined":1593872588,"flights":11605,"contributed":638813,"dailyContribution":25739,"online":1595889439,"shareValue":1830.96},{"company":"Sivas Air","joined":1593945518,"flights":10950,"contributed":592991,"dailyContribution":27854,"online":1595902761,"shareValue":209.51},{"company":"Daegu Airline","joined":1594208963,"flights":5408,"contributed":494707,"dailyContribution":28074,"online":1595904259,"shareValue":1565.28},{"company":"Panthera Leo Air","joined":1594959930,"flights":6014,"contributed":338030,"dailyContribution":33736,"online":1595905238,"shareValue":2166.48},{"company":"MIXO AIR","joined":1595526339,"flights":3765,"contributed":145669,"dailyContribution":23878,"online":1595901281,"shareValue":1084.63},{"company":"PERUVIAN","joined":1595552431,"flights":1295,"contributed":121684,"dailyContribution":29107,"online":1595896216,"shareValue":2161.03}]}
                    if thisData['status']['request'] == 'success':
                        timenow = time.time()
                        remaining = int(thisData['status']['requests_remaining'])
                        if remaining < 25:
                            mode = 'backup1' if mode == 'default' else 'default'
                        del thisData['status']
                        with open('data/log/allianceLog.json', 'r+') as f:
                            oldData = json.load(f)
                            if allianceName not in oldData: # no logs previously, so create a new dict with the data in it.
                                oldData[allianceName] = {f'{timenow}': thisData}
                            else: # append to the log
                                oldData[allianceName][f'{timenow}'] = thisData
                            
                            for alliance in oldData:
                                validLogs = {}
                                for logKey in oldData[alliance]:
                                    thisLogTime = float(logKey)
                                    if thisLogTime > timenow - 1209600: # 14d
                                        validLogs[logKey] = oldData[alliance][logKey]
                                    else:
                                        print(f"{allianceName}'s BOT log at {thisLogTime} has been removed.")
                                oldData[alliance] = validLogs
                                        
                            f.seek(0)
                            json.dump(oldData, f, indent=4)
                            f.truncate()
                        print(f"{mode}.{remaining}: Logged {allianceName}'s details at {timenow}.")

                        # clear variables to conserve RAM.
                        allianceName = None
                        thisData = None
                        timenow = None
                        remaining = None
                        oldData = None
                        alliance = None
                        validLogs = None
                        logKey = None
                        thisLogTime = None
                except:
                    print("ERROR")
            print('=================')
        time.sleep(1800) # until next update
    except:
        time.sleep(1)
