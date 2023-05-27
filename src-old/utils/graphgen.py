import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib import cycler
import time as t
from io import BytesIO
from datetime import datetime
from adjustText import adjust_text
# unused imports?
# import json
# import numpy as np

def svgraph(data, name):
    # plt.style.use('dark_background')
    name = str(name).replace('$', '\$')

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
        'font.family': 'sans-serif',
        'font.sans-serif': 'Baloo Thambi 2',
        'axes.prop_cycle': cycler('color', ['3498db']), # discord blue
        'axes.titlesize': 24,
        'font.size': 12,
        'figure.figsize': (18, 5)
    }) # transparent background plots

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

    # edited it such that it doesn't save the file, instead returns as a bytes-like object.
    buffer = BytesIO()
    plt.savefig(buffer, dpi=100, bbox_inches='tight')
    plt.close('all') # clear up memory
    buffer.seek(0)
    return buffer.read()

    # fig = plt.gcf()
    # plt.savefig("graph.png", dpi=100, bbox_inches='tight')
    # plt.cla()
    # fig.clf()
    # plt.clf()