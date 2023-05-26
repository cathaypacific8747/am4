import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib import cycler
import matplotlib
import time as t
from io import BytesIO
from datetime import datetime
from adjustText import adjust_text
from statistics import mean, median
import math
from colour import Color
from numpy import interp

def statisticsRange(x):
    return sorted(x)[-1] - sorted(x)[0]

def returnStatistics(y, showSum=True):
    temp = r'$\overline{x}$'
    temp += f': {mean(y):,.2f}\n'
    temp += r'$\tilde x$'
    temp += f': {median(y):,.1f}\n'
    temp += r'$x_{max}-x_{min}$'
    temp += f': {statisticsRange(y):,.0f}\n'
    if showSum:
        temp += r'$\sum$'
        temp += f': {sum(y):,.0f}\n'
    return temp

def gradients(x, y):
    return [(y[i+1]-y[i]) / (x[i+1]-x[i]) for i in range(len(y[:-1]))]

def gradientTicks(x):
    return [(x[i+1]+x[i]) / 2 for i in range(len(x[:-1]))]

def regressionGradient(x,y):
    xMean, yMean = mean(x), mean(y)
    return sum([(x[i]-xMean)*(y[i]-yMean) for i in range(len(x))]) / sum([(x[i]-xMean)**2 for i in range(len(x))])

def returnSvStatistics(x,y):
    s = list(filter(lambda x:x != 0, gradients(x,y))) # filter out slopes that's equal to 0.
    try:
        temp = r'$m_{min}$'
        temp += f': \${min(s):.5f}/hr\n'
        temp += r'$m_{reg}$'
        temp += f': \${regressionGradient(x,y):.5f}/hr\n'
        temp += r'$m_{max}$'
        temp += f': \${max(s):.5f}/hr\n'
    except:
        temp = r'$m_{min}$'
        temp += f': \$0/hr\n'
        temp += r'$m_{reg}$'
        temp += f': \$0/hr\n'
        temp += r'$m_{max}$'
        temp += f': \$0/hr\n'
    return temp

def getDiff(x1, y1, x2, y2):
    gapX, gapY = [], []
    for i1 in range(len(x1)):
        try:
            i2 = min(range(len(x2)), key=lambda j:abs(x2[j]-x1[i1]))
            gapX.append((x1[i1]+x2[i2])/2)
            gapY.append(y1[i1]-y2[i2])
        except:
            pass
    return gapX, gapY

def setXticks(oldestHour, interface=plt):
    incrementingHour, diffTicks, displayTicks = 0, [], []
    while incrementingHour >= oldestHour:
        displayText = '' if incrementingHour % 4 else incrementingHour
        displayTicks.append(displayText)
        diffTicks.append(incrementingHour)
        incrementingHour -= 1
    if isinstance(interface, matplotlib.axes._subplots.Subplot):
        interface.set_xticks(diffTicks)
        interface.set_xticklabels(displayTicks)
    else:
        interface.xticks(diffTicks, displayTicks)

def setTransparentBackground():
    plt.rcParams.update({
        # default dark_background.mplstyle
        'lines.color': 'white',
        'text.color': 'white',
        'patch.edgecolor': 'white',
        'axes.edgecolor': 'white',
        'figure.edgecolor': 'black',
        'savefig.edgecolor': 'black',
        'axes.labelcolor': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white',
        'grid.color': 'white',

        # custom styles
        'savefig.facecolor': (1,1,1,0), # border (on_save)
        'figure.facecolor' : (1,1,1,0), # border (on_display)
        'axes.facecolor'   : (1,1,1,0), # inner div
        'legend.framealpha': 0,
        'font.family': 'sans-serif',
        'font.sans-serif': 'Baloo Thambi 2',
        'axes.prop_cycle': cycler('color', ['#3498db', '#f1c40f']), # discord blue
        'axes.titlesize': 24,
        'font.size': 12,
        'figure.figsize': (18, 5),

        # math
        'mathtext.fontset': 'stix' # computer modern
    })

def savefig():
    buffer = BytesIO()
    plt.savefig(buffer, dpi=150, bbox_inches='tight')
    plt.close('all') # clear up memory
    buffer.seek(0)
    return buffer.read()


def svgraph(data, name):
    # plt.style.use('dark_background')
    name = str(name).replace('$', '\$')

    setTransparentBackground()

    def tsToReadable(ts):
        return t.strftime('%d %b, %H:%M', t.gmtime(ts))
    
    def average(x, y, pos):
        return x + ((y - x) / 4 * pos)

    grph = {}
    time, share = [], []
    for obj in data:
        grph[obj['date']] = obj['share']
        time.append(obj['date'])
        share.append(obj['share'])

    plt.plot(time, share, marker='.', markersize=10)
    # plot data labels
    texts = [plt.text(time[i], share[i], f'${share[i]:,.2f}', ha='center', va='center') for i in range(len(time))]    
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='w'))

    plt.title(f'SV history for {name}')
    # plot 5 ticks on the x-axis
    timeticks = [time[0], average(time[0], time[-1], 1), average(time[0], time[-1], 2), average(time[0], time[-1], 3), time[-1]]
    plt.xticks(timeticks, [tsToReadable(i) for i in timeticks])
    plt.xlabel('All times are in GMT')

    return savefig()

def allianceMemberGraph(alliance1, alliance2, mode):
    name1, name2 = f"{alliance1['alliance'][0]['name']}\n", f"{alliance2['alliance'][0]['name']}\n"
    members1, members2 = alliance1['members'], alliance2['members']
    setTransparentBackground()
    
    isContrib = mode == 'contrib'
    if isContrib:
        members1.sort(key=lambda x:x['dailyContribution'], reverse=True)
        members2.sort(key=lambda x:x['dailyContribution'], reverse=True)
    else:
        members1.sort(key=lambda x:x['shareValue'], reverse=True)
        members2.sort(key=lambda x:x['shareValue'], reverse=True)

    percentile1, contributions1, shareValues1, texts1 = [], [], [], []
    for member in members1:
        thisIndex = members1.index(member)
        thisPercentile = thisIndex / (len(members1)-1) * 100
        thisContribution = member['dailyContribution']
        thisShareValue = member['shareValue']
        
        percentile1.append(thisPercentile)
        contributions1.append(thisContribution)
        shareValues1.append(thisShareValue)

        if thisIndex < 5 or thisIndex >= len(members1)-5: 
            # display labels for top 5 and bottom 5 members only.
            if isContrib:
                plt.text(thisPercentile, thisContribution, member['company'], ha='left', va='baseline', rotation=45)
            else:
                plt.text(thisPercentile, thisShareValue, member['company'], ha='left', va='baseline', rotation=45)

    percentile2, contributions2, shareValues2, texts2 = [], [], [], []
    for member in members2:
        thisIndex = members2.index(member)
        thisPercentile = thisIndex / (len(members2)-1) * 100
        thisContribution = member['dailyContribution']
        thisShareValue = member['shareValue']
        
        percentile2.append(thisPercentile)
        contributions2.append(thisContribution)
        shareValues2.append(thisShareValue)

        if thisIndex < 5 or thisIndex >= len(members2)-5:
            # display labels for top 5 and bottom 5 members only.
            if isContrib:
                plt.text(thisPercentile, thisContribution, member['company'], ha='right', va='top', rotation=45)
            else:
                plt.text(thisPercentile, thisShareValue, member['company'], ha='right', va='top', rotation=45)

    if isContrib:
        name1 += returnStatistics(contributions1)
        name2 += returnStatistics(contributions2)

        plt.plot(percentile1, contributions1, marker='.', markersize=10, label=name1)
        plt.plot(percentile2, contributions2, marker='.', markersize=10, label=name2)
        plt.title('Contributions')
        plt.ylabel('Daily Contribution ($)')
        plt.xlabel('Contribution Percentile (%)')
    else:
        name1 += returnStatistics(shareValues1)
        name2 += returnStatistics(shareValues2)

        plt.plot(percentile1, shareValues1, marker='.', markersize=10, label=name1)
        plt.plot(percentile2, shareValues2, marker='.', markersize=10, label=name2)
        plt.title('Share Values')
        plt.ylabel('Share Value ($)')
        plt.xlabel('Share Value Percentile')
        
    plt.legend(loc="upper right", ncol=2, fontsize='large')
  
    return savefig()

def svProgressionGraph(data):
    setTransparentBackground()
    fig, ax1 = plt.subplots()

    lastUpdate = float(sorted(list(data))[-1])  
    hourDiffs = [(float(key)-lastUpdate)/3600 for key in data]
    shareValues = [float(data[key]['alliance'][0]['value']) for key in data]
    
    slopes = gradients(hourDiffs, shareValues)
    ax1.plot(hourDiffs, shareValues, marker='.', markersize=10, label=returnSvStatistics(hourDiffs, shareValues))
    
    ax1.set_title(f"SV Progression for {data[list(data)[-1]]['alliance'][0]['name']}")
    setXticks(min(hourDiffs), ax1)
    
    ax1.set_xlabel(f'Time since {datetime.fromtimestamp(lastUpdate).astimezone().strftime("%d %b %Y %H:%M:%S%z")} (hours)')
    ax1.set_ylabel('Alliance Value ($)')
    leg = ax1.legend(loc='upper left', fontsize='large', handlelength=0, handletextpad=0, markerscale=0)
    for item in leg.legendHandles:
        item.set_visible(False)

    ax2 = ax1.twinx()
    ax2.set_ylabel(r'$\frac{\Delta x}{\Delta t}$' + ' (\$/hour)', alpha=0.7)
    ax2.plot(gradientTicks(hourDiffs), slopes, color=(1,1,1,0.4))
    ax2.tick_params(axis='y', colors=(1,1,1,0.7))

    return savefig()

def svComparisonGraph(data1, data2):
    setTransparentBackground()
    fig, ax1 = plt.subplots()

    #primary y-axis = allianceValue for both alliances
    latestUpdate = max(float(sorted(list(data1))[-1]), float(sorted(list(data2))[-1]))

    allianceName1 = data1[list(data1)[-1]]['alliance'][0]['name']
    hourDiffs1 = [(float(key)-latestUpdate)/3600 for key in data1]
    shareValues1 = [float(data1[key]['alliance'][0]['value']) for key in data1]
    ax1.plot(hourDiffs1, shareValues1, marker='.', markersize=10, label=(f'{allianceName1}\n' + returnSvStatistics(hourDiffs1, shareValues1)))

    allianceName2 = data2[list(data2)[-1]]['alliance'][0]['name']
    hourDiffs2 = [(float(key)-latestUpdate)/3600 for key in data2]
    shareValues2 = [float(data2[key]['alliance'][0]['value']) for key in data2]
    ax1.plot(hourDiffs2, shareValues2, marker='.', markersize=10, label=(f'{allianceName2}\n' + returnSvStatistics(hourDiffs2, shareValues2)))

    # secondary y-axis = allianceValue gap between both of them
    ax2 = ax1.twinx()
    ax2.set_ylabel('Alliance Value Gap (' + r'$\$_'+allianceName1.lower()[:4]+'-\$_'+allianceName2.lower()[:4]+'$' + ')', alpha=0.7)
    gapX, gapY = getDiff(hourDiffs1, shareValues1, hourDiffs2, shareValues2)
    ax2.plot(gapX, gapY, color=(1,1,1,0.4), label=(f'Alliance Value Gap\n' + returnSvStatistics(gapX, gapY)))
    ax2.tick_params(axis='y', colors=(1,1,1,0.7))
    leg = ax2.legend(loc='lower right')
    leg.get_texts()[0].set_color((1,1,1,0.7))

    # titles, axes labels etc.
    ax1.set_title(f"Alliance Value Comparison between {allianceName1} and {allianceName2}")
    setXticks(min(hourDiffs1+hourDiffs2), ax1)
    ax1.set_xlabel(f'Time since {datetime.fromtimestamp(latestUpdate).astimezone().strftime("%d %b %Y %H:%M:%S%z")} (hours)')
    ax1.set_ylabel('Alliance Value ($)')
    ax1.legend(loc='upper left', fontsize='large', ncol=2)

    return savefig()

def contribGraph(data1, data2):
    setTransparentBackground()
    fig, ax1 = plt.subplots()

    latestUpdate = max(float(sorted(list(data1))[-1]), float(sorted(list(data2))[-1]))

    allianceName1 = data1[list(data1)[-1]]['alliance'][0]['name']
    times1 = [(float(key)-latestUpdate)/3600 for key in data1]
    sumOfContribs1 = [sum([int(entry['dailyContribution']) for entry in data1[key]['members']]) for key in data1]
    line1 = ax1.plot(times1, sumOfContribs1, marker='.', markersize=10, label=(f'{allianceName1}\n' + returnStatistics(sumOfContribs1, False) + returnSvStatistics(times1, sumOfContribs1)))

    allianceName2 = data2[list(data2)[-1]]['alliance'][0]['name']
    times2 = [(float(key)-latestUpdate)/3600 for key in data2]
    sumOfContribs2 = [sum([int(entry['dailyContribution']) for entry in data2[key]['members']]) for key in data2]
    line2 = ax1.plot(times2, sumOfContribs2, marker='.', markersize=10, label=(f'{allianceName2}\n' + returnStatistics(sumOfContribs2, False) + returnSvStatistics(times2, sumOfContribs2)))

    ax2 = ax1.twinx()
    gapX, gapY = getDiff(times1, sumOfContribs1, times2, sumOfContribs2)
    line3 = ax2.plot(gapX, gapY, color=(1,1,1,0.4), label=(f'Contribution/day Gap\n' + returnStatistics(gapY, False) + returnSvStatistics(gapX, gapY)))
    ax2.fill_between(gapX, gapY, color=(1,1,1,0.1), interpolate=True)

    # set legends, titles and ticks
    ax2.tick_params(axis='y', colors=(1,1,1,0.7))
    ax1.set_title(f"$\sum$ Contribution/day Comparison between {allianceName1} and {allianceName2}")
    setXticks(min(times1+times2), ax1)
    ax1.set_xlabel(f'Time since {datetime.fromtimestamp(latestUpdate).astimezone().strftime("%d %b %Y %H:%M:%S%z")} (hours)')
    ax1.set_ylabel(r'$\sum$ Total Contribution/day (\$)')
    ax2.set_ylabel(r'Gap in $\sum$ Contribution/day (\$)', alpha=0.7)

    lines = line1+line2+line3
    labels = [l.get_label() for l in lines]
    leg = ax1.legend(lines, labels, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.1))
    leg.get_texts()[2].set_color((1,1,1,0.7))

    return savefig()

def actualContribGraph(data1, data2):
    setTransparentBackground()
    fig, ax1 = plt.subplots()

    latestUpdate = max(float(sorted(list(data1))[-1]), float(sorted(list(data2))[-1]))

    allianceName1 = data1[list(data1)[-1]]['alliance'][0]['name']
    times1, sumOfContribs1 = [], []
    for k in reversed(range(12, len(data1))):
        thisTime = list(data1.keys())[k]
        prevTime = list(data1.keys())[k-12]
        # get (time_now - time_12h_ago)
        dt = (float(thisTime) - float(prevTime)) / 3600

        # get (cont_now - cont_12h_ago)
        thisSum = 0
        for entry in data1[thisTime]['members']:
            for prevEntry in data1[prevTime]['members']:
                if prevEntry['company'] == entry['company']:
                    thisSum += entry['contributed']-prevEntry['contributed']
                    break

        times1.append((float(thisTime)-latestUpdate)/3600)
        sumOfContribs1.append(thisSum/dt)
    line1 = ax1.plot(times1, sumOfContribs1, label=(f'{allianceName1}\n' + returnStatistics(sumOfContribs1, False) + returnSvStatistics(times1, sumOfContribs1)))

    allianceName2 = data2[list(data2)[-1]]['alliance'][0]['name']
    times2, sumOfContribs2 = [], []
    for k in reversed(range(12, len(data2))):
        thisTime = list(data2.keys())[k]
        prevTime = list(data2.keys())[k-12]
        dt = (float(thisTime) - float(prevTime)) / 3600

        thisSum = 0
        for entry in data2[thisTime]['members']:
            for prevEntry in data2[prevTime]['members']:
                if prevEntry['company'] == entry['company']:
                    thisSum += entry['contributed']-prevEntry['contributed']
                    break

        times2.append((float(thisTime)-latestUpdate)/3600)
        sumOfContribs2.append(thisSum/dt)
    line2 = ax1.plot(times2, sumOfContribs2, label=(f'{allianceName2}\n' + returnStatistics(sumOfContribs2, False) + returnSvStatistics(times2, sumOfContribs2)))

    ax2 = ax1.twinx()
    gapX, gapY = getDiff(times1, sumOfContribs1, times2, sumOfContribs2)
    line3 = ax2.plot(gapX, gapY, color=(1,1,1,0.4), label=(f'Contribution/day Gap\n' + returnStatistics(gapY, False) + returnSvStatistics(gapX, gapY)))
    ax2.fill_between(gapX, gapY, color=(1,1,1,0.1), interpolate=True)

    # set legends, titles and ticks
    ax2.tick_params(axis='y', colors=(1,1,1,0.7))
    ax1.set_title(r'$\sum_{n=12}^\infty \frac{c_n-c_{n-12}}{t_n-t_{n-12}}$' + f" Comparison between {allianceName1} and {allianceName2}")
    setXticks(min(times1+times2), ax1)
    ax1.set_xlabel(f'Time since {datetime.fromtimestamp(latestUpdate).astimezone().strftime("%d %b %Y %H:%M:%S%z")} (hours)')
    ax1.set_ylabel(r'$\sum_{n=12}^\infty \frac{c_n-c_{n-12}}{t_n-t_{n-12}}$ (\$/hour)')
    ax2.set_ylabel(r'Gap $\sum_{n=12}^\infty \frac{c_n-c_{n-12}}{t_n-t_{n-12}}$ (\$/hour)', alpha=0.7)

    lines = line1+line2+line3
    labels = [l.get_label() for l in lines]
    leg = ax1.legend(lines, labels, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.1))
    leg.get_texts()[2].set_color((1,1,1,0.7))

    return savefig()

def historicContribGraph(data):
    setTransparentBackground()

    lastUpdate = float(sorted(list(data))[-1])  
    allianceName = data[list(data)[-1]]['alliance'][0]['name']
    memberContribDict = {}
    for key in data:
        for entry in data[key]['members']:
            thisMemberName = entry['company']
            if thisMemberName not in memberContribDict:
                memberContribDict[thisMemberName] = [{
                    'time': (float(key)-lastUpdate)/3600,
                    'value': int(entry['dailyContribution']),
                }]
            else:
                memberContribDict[thisMemberName].append({
                    'time': (float(key)-lastUpdate)/3600,
                    'value': int(entry['dailyContribution']),
                })

    # filter out the current 5 worst-performing airlines
    listOfMemberContribs = []
    for member in memberContribDict:
        latestUpdateValue = sorted(memberContribDict[member], key=lambda x:x['time'])[-1]['value']
        listOfMemberContribs.append((latestUpdateValue, {
            member: memberContribDict[member]
        }))
    
    bottom = sorted(listOfMemberContribs, key=lambda x:x[0])[:5]
    colorGradientList, counter, oldestHours = list(Color('#d16262').range_to(Color('#62afd1'), len(bottom))), 0, []
    for b in bottom:
        thisAirlineName = list(b[1])[0]
        x = [e['time'] for e in b[1][thisAirlineName]]
        y = [e['value'] for e in b[1][thisAirlineName]]
        oldestHours.append(min(x))
        plt.plot(x, y, color=colorGradientList[counter].hex_l, label=thisAirlineName + '\n' + returnStatistics(y, False) + returnSvStatistics(x, y))
        counter += 1

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(bottom))
    setXticks(min(oldestHours))
    plt.title(f'Contrib/day History for the current bottom 5 contributors of {allianceName}')
    plt.ylabel('Contribution/Day ($)')
    plt.xlabel(f'Time since {datetime.fromtimestamp(lastUpdate).astimezone().strftime("%d %b %Y %H:%M:%S%z")} (hours)')

    return savefig()

def dailyContribHistGraph(data, mode):
    setTransparentBackground()

    strings = {
        'dailyContribution': 'Contribution/Day',
        'contributed': 'Contribution',
        'shareValue': 'Share Value'
    }

    graphingInfo = []
    latestUpdate = max(float(sorted(list(data[memberName]))[-1]) for memberName in data)
    for memberName in data:
        times = [(float(time)-latestUpdate)/3600 for time in data[memberName]]
        dailyContribs = [data[memberName][time][mode] for time in data[memberName]]
        graphingInfo.append({
            'name': memberName,
            'times': times,
            mode: dailyContribs,
        })
    
    graphingInfo.sort(key=lambda x:x[mode][-1])
    colorGradientList = list(Color('#d16262').range_to(Color('#62afd1'), len(graphingInfo)))
    for counter in range(len(graphingInfo)):
        x = graphingInfo[counter]['times']
        y = graphingInfo[counter][mode]
        plt.plot(x, y, color=colorGradientList[counter].hex_l, label=graphingInfo[counter]['name'] + '\n' + returnStatistics(y, False) + returnSvStatistics(x, y))
    
    setXticks(min([min(i['times']) for i in graphingInfo]))
    plt.xlabel(f'Time since {datetime.fromtimestamp(latestUpdate).astimezone().strftime("%d %b %Y %H:%M:%S%z")} (hours)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(graphingInfo))
    plt.title(f'{strings[mode]} History for {", ".join([name for name in data])}')
    plt.ylabel(f'{strings[mode]} ($)')
    
    return savefig()