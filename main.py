# -*- coding:utf8 -*-

import requests
from bs4 import BeautifulSoup as bs

import models

host = 'http://www.transfermarkt.co.uk'
fixtures_url = host + '/manchester-city/spielplandatum/verein/281/plus/0'
matchday_url = host + '/soccer/spieltag/wettbewerb/{}/plus/'


def goal_type(goal, history):
    if goal not in history:
        raise Exception


def parse_goals(goals, match):
    score = [0, 0]
#          home away
    winning_goal = None

    for goal in goals.find_all('li'):
        info = goal.find('div', class_='sb-aktion-aktion')
        own_goal = 'Own-goal' in info.text
        home = goal['class'][0] == 'sb-aktion-heim'

        aa = info.find_all('a')
        scorer = aa[0].text
        assist = None
        if len(aa) > 1:
            assist = aa[1].text

        score[not home] += 1

        if home ^ own_goal:  # home player goal
            player = models.Player(match.home, scorer)
        else:
            player = models.Player(match.away, scorer)

        goal = models.Goal(match, player, own_goal, assist)
        match.goals.append(goal)

    print(score)
    for goal in match.goals:
        goal_type(goal, match.goals)
        print(goal.player)


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

    print(th, ta)

    match = models.Match(league, matchday, th, ta)
    league.matches[matchday - 1].append(match)

    goals = match_soup.find('div', id='sb-tore')
    if goals is not None:
        parse_goals(goals, match)


def main():
    s = requests.Session()
    s.headers = {'Host': 'www.transfermarkt.co.uk'}

    leagues = {
        'EPL': 'GB1'
    }

    for year in range(2015, 2016):
        for league, league_id in leagues.items():
            lg = models.League(league, year)
            points_total = {} # 전체 경기수로 normalize?
            points_matchdays = []

            for matchday in range(1, 2):
                lg.matches.append([])
                matches_url = matchday_url.format(league_id)
                r = s.get(matches_url, params={'saison_id': year, 'spieltag': matchday})
                soup = bs(r.content, "lxml")

                reports = soup.find_all('a', title='To match report')
                for report in reports:
                    report_url = host + report['href']
                    r = s.get(report_url)
                    soup = bs(r.content, "lxml")

                    parse_match(soup, lg, matchday)

if __name__ == '__main__':
    main()
