import requests
from lxml import html
import csv
import sys



 
#TODO: Create a set to store old basketball scores

def main():
    base = 'http://www.basketball-reference.com/teams/'
    years = ['2001','2002','2003','2004','2005','2006','2007','2008','2009','2010',
             '2011','2012','2013','2014']
    teams = ['POR', 'LAL', 'DAL', 'SAS', 'SAC', 'OKC', 'GSW', 'CLE', 'LAC',
             'DEN', 'CHH', 'BRK', 'NOP', 'CHI', 'BOS', 'PHI', 'MEM', 'MIN', 'IND', 'NYK',
             'DET', 'MIL', 'HOU', 'TOR', 'ATL', 'MIA', 'ORL', 'PHO', 'WAS', 'UTA']
    data = []
    for year in years:
        for team in teams:
            print team
            print year
            data = generate(data, base, team + '/' + year + '_games.html', {'team': team, 'season': year})
        with open('C:/Users/Jay/Dropbox/Coding Projects/NBA/all_data' + year + '.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, data[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data)
    
#generate a link for the  nba team schedule
def generate(data, base, team, item):
    try:
        response = convert(base + team)
    except:
        print 'No ' + item['team'] + ' in ' + item['season']
    games = response.xpath('//tr')
    for game in games:
        try:
            link = game.xpath("td[@align='center']/a/@href")
            if len(link) > 0:
                item['link'] = get_link(link[0])
                #get a bunch of basic stats from the schedule page
                item = basic_stats(game, item)
                opp_link = game.xpath("td[@align='left']/a/@href")[1]
                item['opp'] = opp_link.split('/')[2]
                resp = convert(item['link'])
                row = resp.xpath('//tr')
                data = parse(row[75:], item, data)
        except:
            print data[len(data)-1]
            print item
    return data

def convert(link):
    raw = requests.get(link).content
    return html.fromstring(raw)

def get_link(link):
    pbp_base = 'http://www.basketball-reference.com/boxscores/pbp/'
    #TODO: Check if it's in a set so to skip
    values = link.split('/')
    return pbp_base + values[2]

def basic_stats(game, item):
    stats = game.xpath("td/text()")
    item['gametime'] = stats[1]
    if stats[2] == '@' or stats[3] =='@':
        item['away'] = 1
    else:
        item['away'] = 0
    item['team score'], item['opp score'] = stats[len(stats)-5], stats[len(stats)-4]
    item['wins'], item['losses'], item['streak'] = stats[len(stats)-3], stats[len(stats)-2], stats[len(stats)-1]
    return item

def parse(times, item, data):
    i = 0
    while i < len(times):
        #print i
        if item['away'] == 0:
            num = twoForOne(times, i, 5) 
        else:
            num = twoForOne(times, i, 1)
        if num is not None:
            #TODO differential
            i, item = getData(times, i, item, num)
            data.append(item.copy())
        i += 1
    return data


def getHour(xml):
    time = xml.xpath('td/text()')
    return time[0].split(':') if len(time) > 0 else ['No', 'No']
 
def shot(xml, num):
    if len(xml) >= 6:
        if any([x in xml[num] for x in 
            ['misses 2-pt', 'misses 3-pt', 'Shooting foul', 'makes 3-pt', 'makes 2-pt']]):
            return num
#any([x in data['title'][index].lower() for x in titleGood])
def twoForOne(times, i, away):
    minute = getHour(times[i])
    #check to see if it's within the timeline of a 2 for 1
    if minute[0] == '0' and float(minute[1]) > 25 and float(minute[1]) < 39:
        #Check to see if the resulting action is of a 2 for 1
        #print item
        num = shot(times[i].xpath('td/text()'), away)
        return num if num else None

def get_score(xml):
    for color in ['white', 'aqua', 'yellow']:
        if len(xml.xpath('td[@class="align_center background_' + color + '"]/text()')) > 0:
            return xml.xpath('td[@class="align_center background_' + color + '"]/text()')[0]


def getData(times, i, item, num):
    make = times[i].xpath('td[@class="background_lime"]')
    miss = times[i].xpath('td[@class="background_white"]')
    if len(make) < 1:
        item = make_miss(False, item, miss[0])
        item = switch(get_score(times[i]).split('-'), item, 'shot_score')
    else:
        item = make_miss(True, item, make[0])
        item = switch(get_score(times[i-1]).split('-'), item, 'shot_score')
    item['clock'] = getHour(times[i])[1]
    item['shot clock'] = 24.0 - (float(getHour(times[i-1])[1]) - float(item['clock']))
    return last_shot(times, i,item)

def switch(xml, item, name):
    if item['away'] == 0:
        item['team_' + name] = xml[1]
        item['opp_' + name] = xml[0]
    else:
        item['team_' + name] = xml[0]
        item['opp_' + name] = xml[1]
    return item
    
def last_shot(times, i, item):
    while 'End' not in times[i].xpath('td/text()')[1]:
        i += 1
    #import pdb; pdb.set_trace()
    item = switch(get_score(times[i-1]).split('-'), item, 'q_score')
    item['quarter'] = times[i].xpath('td/text()')[1]
    return i, item
    
def make_miss(attempt, item, player):
    item['made'] = attempt
    item['player'] = player.xpath('a/text()')[0]
    item['shot'] = player.xpath('text()')[0]
    return item

            