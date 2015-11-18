# -*- coding:utf8 -*-

import os
import time
from collections import Counter

import requests
from bs4 import BeautifulSoup as bs
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'soccerstat.settings'
django.setup()


from soccerstat.models import *


def main():
    leagues = {
        'EPL': 'GB1',
        'La Liga': 'ES1',
    }
    goals = []
    assists = []
    for year in range(2015, 2016):
        for league, league_id in leagues.items():
            lg, created = League.objects.get_or_create(name=league, year=year)

            top_goal = Counter()
            top_assist = Counter()
            for club in Club.objects.filter(league=lg):
                print(club)
                for contract in Contract.objects.filter(club=club):
                    player = contract.player
                    goals.append(player.goal_point())
                    assists.append(player.assist_point())
                    top_goal[player.name] += player.goal_point()
                    top_assist[player.name] += player.assist_point()

            print('Goal Top 20')
            for k, v in top_goal.most_common(20):
                print (k,v)

            print('Assist Top 20')
            for k, v in top_assist.most_common(20):
                print (k, v)

if __name__ == '__main__':
    main()
