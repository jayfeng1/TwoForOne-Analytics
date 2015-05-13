# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:17:47 2015

@author: Jay
"""

import pandas as pd
from ggplot import *
import numpy as np
import scipy.stats as stats
import pylab as pl
import seaborn as sns
from matplotlib import pyplot

'''Things to look into:
    - 
    - Gain in points for best time to go for the two-for-one
        - subset that into different quarters
    - Does the two-for-one in the third quarter help with a win in the fourth
        - when made or missed
        - when only made
    - Seaborn matrix on optimized gain on shot clock and game clock
    - Gain on differential on score shot
    - Plot the distribution of game
    - Plot each team and how often they did the two for one over the years
    - Write about vs the clippers now and how to analyze their play style
    - End game analysis
    - Create a dashboard
    - Plot line graph of clock time and gain for each second in the shot clock so
        teams can follow the line and track where it would be most effective for the 
        time they are at
    - Predictive Model with logistic regression to figure out best time:
        -categorize and group time and shot clock values
'''
fifteen = pd.read_csv('/Users/Jay/Dropbox/Coding Projects/NBA/twoForOne.csv')
data = pd.read_csv('/Users/Jay/Dropbox/Coding Projects/NBA/all_data.csv')
por = fifteen[fifteen['team'] == 'POR']



def average(data, time, f):
    clocks = pd.DataFrame(data[time].value_counts())
    clocks = clocks.sort(ascending=False)
    clocks['gain'] = 0
    for value in clocks.index:
        clocks.ix[value, 'gain'] = f(data[data[time] == value]['diff_gain'])
    return clocks

def seaborn_matrix(data, group, group2):
    table = pd.DataFrame(data[group].value_counts()).sort_index()
    crimes = list(table.index.values)
    for crime in crimes:
        crime2 = pd.DataFrame(data[data[group] == crime][group2].value_counts()).sort_index(ascending=False)
        headers = list(crime2.index.values)
        #Place headers in dataframe
        for head in headers:
            if head not in list(table.columns):
                table[head] = 0
            #print head
            #table.loc[crime, head] = crime2.loc[head][0]
            table.loc[crime, head] = int(100*mean(data[(data[group] == crime) & (data[group2] == head)]['diff_gain']))
    return table

'''INITIAL ANALYSIS:
    - fouls lead to higher gain?
    - take a foul and then get the possesion back for james
        - lebron james:
            40-40: foul him, then run 2 for 1.
                - Lebron shoots 1.5, 2 for 1 gain of .8, down -.7
            - don't foul
                - Lebron gain of .8 
'''
foul = data[data.type == 'foul']
no_foul = data[data.type != 'foul']
lebron = data[data.player== 'L. James']
mean(lebron.diff_gain)


clocks = average(fifteen, 'clock', mean)
clocks['gain'].plot(ylim = [0,1], figsize=(18, 14))
shot_clock = average('shot_clock')
plot = shot_clock['gain'].plot(ylim = [0,1.75], figsize=(15,10))
plot.set_xlabel('Shot Clock in Seconds')
plot.set_ylabel('Gain in Points at the End of the Quarter')

sns.set_context("poster")
plt.figure(figsize=(8, 6))


urgent = data[data.clock + (24 - data['shot_clock']) < 35]
check_urgent = urgent[(urgent.quarter != 'End of 4th quarter') & (urgent['shot_clock'] < 19)]

wins = data[data.diff_score > 0]
third = data[data.quarter == 'End of 3rd quarter']
thirdAndclose = third[abs(third.diff_q_score) < 10]
gaining = thirdAndclose[thirdAndclose.diff_shot_score > thirdAndclose.diff_score]

''' players analysis'''
players = fifteen[fifteen.type != 'foul']
players['player'].value_counts()
beard = players[players.player == 'J. Harden']
hou = players[players.team == 'HOU']
lac = players[players.team == 'LAC']
dist_bins = np.linspace(0, 30, 31)
pyplot.hist(list(hou.distance), dist_bins, label='HOU')
pyplot.hist(list(lac.distance), dist_bins, label='LAC')
pyplot.legend(loc='upper right')

'''End Game Analysis'''

