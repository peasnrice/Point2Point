from Point2Point import settings
from django.db import models
from datetime import datetime, time
from django.utils.timezone import utc
from django.forms import ModelForm
from django.db.models import Count
from pytz import timezone
import pytz
from django.db import models
import timedelta

class Competition(models.Model):
    name = models.CharField(max_length=32)
    start_destination = models.CharField(max_length=140)
    description = models.CharField(max_length=512)
    greeting = models.CharField(max_length=140)
    congratulation = models.CharField(max_length=140)
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
        montreal = timezone('America/Montreal')
        current_date = datetime.utcnow().replace(tzinfo=montreal)
        new_game_instance = GameInstance(competition = self, current_question = 0, 
                     started = False, ended = False) 
        new_game_instance.save()
        new_game_instance.team_set.add(Team.objects.get(id=team_id_))
        self.gameinstance_set.add(GameInstance.objects.get(id=new_game_instance.id))
    def getGameInstances(self):
        return GameInstance.objects.filter(competition=self.id)
    def __unicode__(self):
        return self.name

class GameInstance(models.Model):
    competition = models.ForeignKey('Competition')
    total_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    game_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    current_question = models.IntegerField()
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    __pauseStartTime = datetime
    #returns time from start to finish, including break/pause time
    def getTotalTime(self):
        start_time = GameStage.objects.filter(gameinstance=self.id).earliest("id").start_time
        end_time = GameStage.objects.filter(gameinstance=self.id).latest("id").start_time
        game_stages = GameStage.objects.filter(gameinstance=self.id).order_by("id")
        time_delta = game_stages[0].start_time - game_stages[0].start_time
        for i in range(len(game_stages)-1):
            time_delta += game_stages[i+1].start_time - game_stages[i].start_time
        return time_delta
    #returns time excluding break/pause time
    def getGameTime(self):
        start_time = GameStage.objects.filter(gameinstance=self.id).earliest("id").start_time
        end_time = GameStage.objects.filter(gameinstance=self.id).latest("id").start_time
        game_stages = GameStage.objects.filter(gameinstance=self.id).order_by("id")
        time_delta = game_stages[0].start_time - game_stages[0].start_time
        for i in range(len(game_stages)-1):
            if game_stages[i].is_pause == False:
                time_delta += game_stages[i+1].start_time - game_stages[i].start_time
        return time_delta
    def getTeam(self):
        return Team.objects.filter(gameinstance=self.id)[0]
    def createGameStage(self):
        competition = self.competition
        questions_query = QuestionsSolutionPair.objects.filter(competition=competition)
        if len(questions_query) > self.current_question:
            question = questions_query.get(question_number=self.current_question)
            new_game_stage_instance = GameStage(gameinstance = self, stage = self.current_question, is_pause = question.is_pause)
        else:
            new_game_stage_instance = GameStage(gameinstance = self, stage = self.current_question, is_pause = True)
        new_game_stage_instance.save()
        self.gamestage_set.add(GameStage.objects.get(id=new_game_stage_instance.id))      
    def __unicode__(self):
        return "COMP: " + str(self.competition.name) + " - ID: " + str(self.id)

class GameStage(models.Model):
    gameinstance = models.ForeignKey('GameInstance')
    stage = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    Penalty = models.IntegerField(default=0)
    is_pause = models.BooleanField(default=False)
    def __unicode__(self):
        return "COMP: " + str(self.gameinstance.competition.name) + "- GAME INST: " + str(self.gameinstance.id) + " - STAGE: " + str(self.stage) + " - TIME STAMP: " + str(self.start_time)

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
    question_text = models.CharField(max_length=140)
    is_pause = models.BooleanField(default=False)
    def __unicode__(self):
        return "COMP: " + str(self.competition.name) + " - Q#: " + str(self.question_number)

class Solution(models.Model):
    questions_solution_pair = models.ForeignKey('QuestionsSolutionPair')
    solution_text = models.CharField(max_length=32)
    def __unicode__(self):
        return self.solution_text
