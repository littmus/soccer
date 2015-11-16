from django.db import models

class League(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    year = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return '{} - {}'.format(self.year, self.name)


class Player(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name

    def goal_point(self, round=None):
        p = 0
        scores = Scored.objects.filter(scorer=self)
        if round:
            scores.filter(match__round=round)

        for score in scores:
            p += score.goal.point

        return p

    def assist_point(self, round=None):
        p = 0
        scores = Scored.objects.filter(assist=self)
        if round:
            scores.filter(match__round=round)

        for score in scores:
            p += score.goal.point

        return p


class Club(models.Model):
    league = models.ForeignKey(League)
    name = models.CharField(max_length=50, null=False, blank=False)
    players = models.ManyToManyField(Player, through='Contract')

    def __str__(self):
        return '{} - {}'.format(self.league.name, self.name)


class Contract(models.Model):
    club = models.ForeignKey(Club)
    player = models.ForeignKey(Player)

    def __str__(self):
        return '{} - {}'.format(self.club, self.player, self.year)


class Goal(models.Model):
    TYPES = (
        ('G', 'Goal'),
        ('E', 'Equalizer'),
        ('T', 'Turnover'),
        ('W', 'Winning'),
    )
    TYPE_POINTS = {
        'G': 0.5,
        'E': 1.5,
        'T': 2.0,
        'W': 3.0,
    }

    own_goal = models.BooleanField()
    point = models.FloatField(default=0.5)
    type = models.CharField(max_length=1, choices=TYPES, default='G')

    def save(self, *args, **kwargs):
        self.point = self.TYPE_POINTS.get(self.type, 0.5)
        if self.own_goal:
            self.point *= -1

        super(Goal, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} {}'.format(' (O.G)' if self.own_goal else '', self.type, self.point)


class Match(models.Model):
    league = models.ForeignKey(League)
    round = models.IntegerField()
    home = models.ForeignKey(Club, related_name='home')
    away = models.ForeignKey(Club, related_name='away')
    goals = models.ManyToManyField(Goal, through='Scored', through_fields=('match', 'goal'))

    def __repr__(self):
        return '{} ({}) {} vs {}'.format(self.league, self.round, self.home.name, self.away.name)


class Scored(models.Model):
    match = models.ForeignKey(Match)
    goal = models.ForeignKey(Goal)
    scorer = models.ForeignKey(Player, related_name='scorer', null=False)
    assist = models.ForeignKey(Player, related_name='assist', null=True, default=None)

    def __str__(self):
        return '{} - {}{}'.format(self.match, self.scorer, self.goal)
    """
    def save(self, *args, **kwargs):
        self.scorer.goal_point += self.goal.point
        self.scorer.
        self.scorer.
        if self.assist:
            self.assist.assist_point += self.goal.point

        super(Scored, self).save(*args, **kwargs)

def update_player_score(sender, instance, created, **kwargs):
    scorer = Player.objects.get(id=instance.scorer.id)
    scorer.goal_point += instance.goal.point
    scorer.save()

models.signals.post_save.connect(update_player_score, sender=Scored)
    """
