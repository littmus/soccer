# -*- coding:utf8 -*-

from collections import defaultdict, Counter

import requests
from bs4 import BeautifulSoup as bs

import models

host = 'http://www.transfermarkt.co.uk'
fixtures_url = host + '/manchester-city/spielplandatum/verein/281/plus/0'
matchday_url = host + '/soccer/spieltag/wettbewerb/{}/plus/'


def goal_type(goal, history):
    if goal not in history:
        raise Exception


def parse_goals(goal_data, match):
    HOME = False
    AWAY = True
    
    goals = []
    score = [0, 0]
#          home away
    winning_candidates = []
    prev_leading = None

    for goal in goal_data.find_all('li'):
        info = goal.find('div', class_='sb-aktion-aktion')
        
        club = goal['class'][0] == 'sb-aktion-gast'
        own_goal = 'Own-goal' in info.text

        aa = info.find_all('a')
        scorer = aa[0].text.strip()
        assist = None
        if len(aa) > 1:
            assist = aa[1].text.strip()
        
        score[club] += 1
        if club ^ own_goal:  # away player goal
            player = models.Player(match.away, scorer)
        else:  # home player goal
            player = models.Player(match.home, scorer)
        
        goal = models.Goal(match, player, own_goal, assist)
        goals.append(goal)

        leading = None if score[HOME] == score[AWAY] else score[HOME] < score[AWAY]
        
        if prev_leading is None:
            if sum(score) == 1: # winning candidate
                pass
            else: # turnover, winning candidate
                goal.type = 'turnover'

            winning_candidates.append(len(goals))
        else:
            if leading is None: # equalizer
                goal.type = 'equalizer'

                winning_candidates.pop(0)
            else: # normal goal
                if leading == club ^ own_goal: # chase goal
                    winning_candidates.append(len(goals))
                else:
                    winning_candidates.pop(0)

        prev_leading = leading
        
    winning_goal = None
    if winning_candidates:
        winning_goal = winning_candidates.pop(0)
        goals[winning_goal - 1].type = 'winning'

    for goal in goals:
        if goal.type == 'goal':
            pass
        elif goal.type == 'equalizer':
            goal.point = 1.5
        elif goal.type == 'turnover':
            goal.point = 2
        elif goal.type == 'winning':
            goal.point = 3

        if goal.own_goal:
            goal.point *= -1

    return goals

def parse_match(match_soup, league, matchday):
    c = match_soup.find_all('div', class_='sb-team')
    th = c[0].find('a')['title']
    ta = c[2].find('a')['title']

    if th not in league.clubs:
        league.clubs[th] = models.Club(league, th)
    th = league.clubs[th]

    if ta not in league.clubs:
        league.clubs[ta] = models.Club(league, ta)
    ta = league.clubs[ta]

    match = models.Match(league, matchday, th, ta)

    goals = match_soup.find('div', id='sb-tore')
    if goals is not None:
        match.goals = parse_goals(goals, match)

    return match

def main():
    s = requests.Session()
    s.headers = {'Host': 'www.transfermarkt.co.uk'}

    leagues = {
        'EPL': 'GB1'
    }

    for year in range(2015, 2016):
        for league, league_id in leagues.items():
            lg = models.League(league, year)
            points_total = Counter()  # 전체 경기수로 normalize?
            points_matchdays = []

            for matchday in range(1, 13):
                matches = []
                points_matchday = defaultdict(float)

                matches_url = matchday_url.format(league_id)
                r = s.get(matches_url, params={'saison_id': year, 'spieltag': matchday})
                soup = bs(r.content, "lxml")

                reports = soup.find_all('a', title='To match report')
                for report in reports:
                    report_url = host + report['href']
                    r = s.get(report_url)
                    soup = bs(r.content, "lxml")

                    match = parse_match(soup, lg, matchday)
                    matches.append(match)

                    for goal in match.goals:
                        points_matchday[goal.player] += goal.point
                
                lg.matches.append(matches)
                points_matchdays.append(points_matchday)
            
            for points_matchday in points_matchdays:
                points_total.update(points_matchday)

            for player, point in points_total.items():
                print(player, ':', point)

if __name__ == '__main__':
    main()
