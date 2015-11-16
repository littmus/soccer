# -*- coding:utf8 -*-

import os
import time

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup as bs
import django


os.environ['DJANGO_SETTINGS_MODULE'] = 'soccerstat.settings'
django.setup()


from soccerstat.models import *


host = 'http://www.transfermarkt.co.uk'
matchday_url = host + '/soccer/spieltag/wettbewerb/{}/plus/'


def parse_goals(goal_data, match):
    HOME = False
    AWAY = True

    goals = []
    score = [0, 0]
#          home away
    winning_candidates = []
    prev_leading = None

    for g in goal_data.find_all('li'):
        info = g.find('div', class_='sb-aktion-aktion')
        club = g['class'][0] == 'sb-aktion-gast'
        own_goal = 'Own-goal' in info.text

        aa = info.find_all('a')
        scorer = aa[0].text.strip()
        assist = None
        if len(aa) > 1:
            name = aa[1].text.strip()
            assist, created = Player.objects.get_or_create(name=name)
            if created:
                assist_club = match.home if club ^ own_goal else match.away
                contract = Contract.objects.create(club=assist_club, player=assist)

        score[club] += 1
        player, created = Player.objects.get_or_create(name=scorer)
        if created:
            player_club = match.away if club ^ own_goal else match.home
            contract = Contract.objects.create(club=player_club, player=player)

        goal = Goal(own_goal=own_goal)
        goals.append(goal)

        if score[HOME] == score[AWAY]:
            leading = None
        else:
            leading = score[HOME] < score[AWAY]

        if prev_leading is None:
            if sum(score) > 1:  # turnover, winning candidate
                goal.type = 'T'
            winning_candidates.append(len(goals))
        else:
            if leading is None:  # equalizer
                goal.type = 'E'
                winning_candidates.pop(0)
            else:  # normal goal
                if leading == club ^ own_goal:  # chase goal
                    winning_candidates.append(len(goals))
                else:
                    winning_candidates.pop(0)

        goal.save()
        scored = Scored.objects.create(match=match, goal=goal, scorer=player, assist=assist)
        prev_leading = leading

    winning_goal = None
    if winning_candidates:
        winning_goal = goals[winning_candidates.pop(0) - 1]
        winning_goal.type = 'W'
        winning_goal.save()


def parse_match(match_soup, league, matchday):
    c = match_soup.find_all('div', class_='sb-team')
    th = c[0].find('a')['title'].strip()
    ta = c[2].find('a')['title'].strip()

    club_home, created = Club.objects.get_or_create(league=league, name=th)
    club_away, created = Club.objects.get_or_create(league=league, name=ta)

    match, created = Match.objects.get_or_create(league=league, round=matchday, home=club_home, away=club_away)

    goals = match_soup.find('div', id='sb-tore')
    if goals is not None:
        parse_goals(goals, match)


def main():
    s = requests.Session()
    s.headers = {'Host': 'www.transfermartk.co.uk'}
    s.mount('http://www.transfermarkt.co.uk', HTTPAdapter(max_retries=5))

    leagues = {
#        'EPL': 'GB1',
        'La Liga': 'ES1',
    }

    for year in range(2015, 2016):
        for league, league_id in leagues.items():
            lg, created = League.objects.get_or_create(name=league, year=year)
            for matchday in range(1, 12):
                matches_url = matchday_url.format(league_id)
                r = s.get(matches_url, params={'saison_id': year, 'spieltag': matchday})
                soup = bs(r.content, "lxml")

                reports = soup.find_all('a', title='To match report')
                for report in reports:
                    report_url = host + report['href']
                    r = s.get(report_url)
                    soup = bs(r.content, "lxml")

                    parse_match(soup, lg, matchday)

                time.sleep(0.5)

            for player in Player.objects.all():
                print(player, ':', player.goal_point())


if __name__ == '__main__':
    main()
