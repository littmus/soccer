class League(object):

    def __init__(self, name, year):
        self.name = name
        self.year = year
        self.clubs = {}
        self.matches = []

    def __repr__(self):
        return '{} - {}'.format(self.year, self.name)


class Club(object):

    def __init__(self, league, name):
        self.league = league
        self.name = name
        self.players = []

    def __repr__(self):
        return '{} - {}'.format(self.league.name, self.name)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, Club):
            return str(self) == str(other)
        else:
            return False



class Player(object):

    def __init__(self, club, name):
        self.club = club
        self.name = name
        self.goal_point = 0
        self.assist_point = 0
        self.goals = []

    def __repr__(self):
        return '{} - {}'.format(self.club.name, self.name)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, Player):
            return str(self) == str(other)
        else:
            return False


class Match(object):

    def __init__(self, league, round, home, away):
        self.league = league
        self.round = round
        self.home = home
        self.away = away
        self.home_goals = []
        self.away_goals = []
        self.goals = []

    def __repr__(self):
        return '{} ({}) {} vs {}'.format(self.league, self.round, self.home.name, self.away.name)

class Goal(object):

    def __init__(self, match, player, own_goal=False, assist=None):
        self.match = match
        self.player = player
        self.own_goal = own_goal
        self.assist = assist
        self.type = 'goal'
        self.point = 0.5

    def __repr__(self):
        return '{} - {}{} {} {}'.format(self.match, self.player, ' (O.G)' if self.own_goal else '', self.type, self.point)
