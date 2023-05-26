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

token = '***REMOVED***'
http = urllib3.PoolManager()

def getDokdoName(userid):
    try:
        thisData = json.loads(http.request('GET', f'https://www.airline4.net/api/?access_token={token}&id={userid}').data.decode('utf-8'))
        return thisData['user']['alliance']
    except:
        return 'Dokdo'

def reqAlliance(allianceName):
    try:
        thisData = json.loads(http.request('GET', f'https://www.airline4.net/api/?access_token={token}&search={quote(allianceName)}').data.decode('utf-8'))
        if thisData['status']['request'] != 'success':
            raise ValueError()
        del thisData['status']
        return thisData
    except:
        return {}

while 1:
    # try:
    with open('data/watchlist.csv', 'r', encoding='utf-8') as g:
        watchlist = g.read().split(',')
        watchlist.append(getDokdoName(225150))
        for _, allianceName in enumerate(watchlist):
            try:
                thisData = reqAlliance(allianceName)
                if thisData != {}:
                    if _ == len(watchlist) - 1:
                        allianceName = 'Dokdo'

                    timenow = time.time()
                    with open('data/log/allianceLog.json', 'r+', encoding='utf-8') as f:
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
                    print(f"Logged {allianceName}'s details at {timenow}.")

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
    time.sleep(3600) # until next update
    # except:
    #     time.sleep(2)
