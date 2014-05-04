from Point2Point import settings
from django.db import models
from datetime import datetime, time
from django.utils.timezone import utc
from django.forms import ModelForm
from django.db.models import Count
from django.db import models
import timedelta, datetime

class Competition(models.Model):
    name = models.CharField(max_length=512)
    start_destination = models.CharField(max_length=512)
    description = models.CharField(max_length=512)
    greeting = models.CharField(max_length=512)
    congratulation = models.CharField(max_length=512)
    estimated_duration = models.IntegerField()
    team_size_limit = models.IntegerField()
    creators_name = models.CharField(max_length=32)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)
    def getQSPairTextByQNum(self, question_number_):
        questions = QuestionsSolutionPair.objects.filter(competition=self.id)
        return questions.get(question_number=question_number_).question_text
    def getQuestLength(self):
        return QuestionsSolutionPair.objects.filter(competition=self.id).count()-1
    def getQuestion(self, question_number_):
        return QuestionsSolutionPair.objects.filter(competition=self.id).get(question_number=question_number_).question_text
    def getSolutions(self, question_number_):
        questions = QuestionsSolutionPair.objects.filter(competition=self.id)
        question = questions.get(question_number=question_number_)
        return Solution.objects.filter(questions_solution_pair=question.id)
    def createGameInstance(self, team_id_):
        new_game_instance = GameInstance(competition = self, current_question = 0, 
                     started = False, ended = False, total_time=datetime.timedelta(seconds=0),
                        average_time=datetime.timedelta(seconds=0),penalty_time=datetime.timedelta(seconds=0),
                            game_time=datetime.timedelta(seconds=0)) 
        new_game_instance.save()
        new_game_instance.team_set.add(Team.objects.get(id=team_id_))
        self.gameinstance_set.add(GameInstance.objects.get(id=new_game_instance.id))
        return new_game_instance
    def getGameInstances(self):
        return GameInstance.objects.filter(competition=self.id)
    def __unicode__(self):
        return self.name

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

class GameInstance(models.Model):
    competition = models.ForeignKey('Competition')
    total_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    game_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    penalty_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    average_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    current_question = models.IntegerField()

    # keeps ongoing record of life lines and incorrect answers
    incorrect_answers = models.IntegerField(default=0)
    location_hints_used = models.IntegerField(default=0)
    clue_hints_used = models.IntegerField(default=0)

    # keeps track of number of incorrect answers answered within the current question
    # there isn't really a need to store this in the db, so long as the server stays up,
    # it isn't a problem
    answered_incorrectly = models.BooleanField(default=False)
    clue_hint_used = models.BooleanField(default=False)
    location_hint_used = models.BooleanField(default=False)

    #keeps track of game state
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    dnf = models.BooleanField(default=False)
    __pauseStartTime = datetime

    #returns time excluding break/pause time
    def getGameTime(self):
        game_stages = GameStage.objects.filter(gameinstance=self.id).order_by("id")
        time_delta = datetime.timedelta(0)
        for i in range(len(game_stages)-1):
            if game_stages[i].is_pause == False:
                time_delta += game_stages[i+1].time_stamp - game_stages[i].time_stamp
        return time_delta 
    #returns time from start to finish, including break/pause time
    def getTotalTime(self):
        return self.getGameTime() + self.penalty_time
    def getAverageTime(self):
        game_stages = GameStage.objects.filter(gameinstance=self.id).order_by("id")
        time_delta = datetime.timedelta(0)
        questions = 0
        for i in range(len(game_stages)-1):
            if game_stages[i].is_pause == False:
                questions += 1
        if questions == 0:
            time_delta = 0
        else:
            time_delta = (self.getGameTime()+self.penalty_time)/questions
        return time_delta         
    def updateGameTime(self):
        self.game_time = self.getGameTime()
        self.total_time = self.getTotalTime()
        self.average_time = self.getAverageTime()
        self.save()
    def getTimeAsText(self):
        average_time = strfdelta(self.average_time, "{hours}h {minutes}m {seconds}s")
        game_time = strfdelta(self.game_time, "{hours}h {minutes}m {seconds}s")
        penalty_time = strfdelta(self.penalty_time, "{hours}h {minutes}m {seconds}s")

        return average_time, game_time, penalty_time


    def addPenalty(self,mins):
        game_stage = GameStage.objects.filter(gameinstance=self.id).get(stage=self.current_question)
        game_stage.penalty += mins
        game_stage.save()
    def getTeamName(self):
        return Team.objects.get(gameinstance=self.id)
    def createGameStage(self):
        competition = self.competition
        questions_query = QuestionsSolutionPair.objects.filter(competition=competition)
        if len(questions_query) > self.current_question:
            question = questions_query.get(question_number=self.current_question)
            new_game_stage_instance = GameStage(gameinstance = self, stage = self.current_question, is_pause = question.is_pause,
                                                answered_incorrectly = self.answered_incorrectly, clue_hint_used = self.clue_hint_used,
                                                location_hint_used = self.location_hint_used)
        else:
            new_game_stage_instance = GameStage(gameinstance = self, stage = self.current_question, is_pause = True,
                                                answered_incorrectly = self.answered_incorrectly, clue_hint_used = self.clue_hint_used,
                                                location_hint_used = self.location_hint_used)
        new_game_stage_instance.save()
        self.gamestage_set.add(GameStage.objects.get(id=new_game_stage_instance.id))
    def __unicode__(self):
        return "COMP: " + str(self.competition.name) + " - ID: " + str(self.id)

class GameStage(models.Model):
    gameinstance = models.ForeignKey('GameInstance')
    stage = models.IntegerField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    penalty = models.IntegerField(default=0)
    is_pause = models.BooleanField(default=False)
    answered_incorrectly = models.BooleanField(default=False)
    clue_hint_used = models.BooleanField(default=False)
    location_hint_used = models.BooleanField(default=False)
    def __unicode__(self):
        return "COMP: " + str(self.gameinstance.competition.name) + "- GAME INST: " + str(self.gameinstance.id) + " - STAGE: " + str(self.stage) + " - TIME STAMP: " + str(self.time_stamp)

class Team(models.Model):
    gameinstance = models.ForeignKey('GameInstance', blank=True, null=True)
    name = models.CharField(max_length=32)
    captain_name = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=12)
    email = models.EmailField(null=True, blank=True)
    def addPlayer(self, phone_number_, name_, email_):
        plyr = Player(first_name = name_, phone_number = phone_number_, email = email_)
        plyr.save()
        self.player_set.add(Player.objects.get(id=plyr.id))      
    def getPlayers(self):
        return Player.objects.filter(team=self.id)
    def __unicode__(self):
        return self.name

class Player(models.Model):
    team = models.ForeignKey('Team', blank=True, null=True)
    phone_number = models.CharField(max_length=12)
    name = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    def __unicode__(self):
        return self.phone_number

class QuestionsSolutionPair(models.Model):
    competition = models.ForeignKey('Competition')
    question_number = models.IntegerField()
    question_text = models.CharField(max_length=512)
    clue_hint_text = models.CharField(max_length=512)
    location_hint_text = models.CharField(max_length=512)
    is_pause = models.BooleanField(default=False)
    def __unicode__(self):
        return "COMP: " + str(self.competition.name) + " - Q#: " + str(self.question_number)

class Solution(models.Model):
    questions_solution_pair = models.ForeignKey('QuestionsSolutionPair')
    solution_text = models.CharField(max_length=64)
    def __unicode__(self):
        return self.solution_text
