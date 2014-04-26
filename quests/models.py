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
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    start_destination = models.CharField(max_length=140)
    description = models.CharField(max_length=512)
    greeting = models.CharField(max_length=140)
    congratulation = models.CharField(max_length=140)
    estimated_duration = models.IntegerField()
    team_size_limit = models.IntegerField()
    creators_name = models.CharField(max_length=32)
    date_created = models.DateTimeField(auto_now_add=True)
    def addQuestionSolutionPair(self, question_, solutions_):
        return null
    def getNumberOfQuestions(self):
        questions = Competition.objects.annotate(num_questions=Count('QuestionsSolutionPair'))
        return questions[0].num_questions
    def getQuestionSolutionPairsByQNum(self, question_number_):
        return QuestionsSolutionPair.objects.select_related("competition").filter(question_number=question_number_)
    def getQSPairTextByQNum(self, question_number_):
        return QuestionsSolutionPair.objects.select_related("competition").get(question_number=question_number_).question_text

    def getQuestLength(self):
        return QuestionsSolutionPair.objects.select_related("competition").all().count()-1

    def getQuestion(self, question_number_):
        return QuestionsSolutionPair.objects.select_related("competition").get(question_number=question_number_).question_text

    def getSolutions(self, question_number_):
        question = QuestionsSolutionPair.objects.select_related("competition").get(question_number=question_number_)
        return Solution.objects.select_related("questions_solution_pair").filter(questions_solution_pair=question.id)

    def createGameInstance(self, team_id_):
        montreal = timezone('America/Montreal')
        current_date = datetime.utcnow().replace(tzinfo=montreal)
        new_game_instance = GameInstance(competition = self, start_time = current_date, end_time = current_date, 
                     pause_time = 0, total_time = 0, current_question = 0, 
                     started = False, paused = False, ended = False) 
        new_game_instance.save()
        new_game_instance.team_set.add(Team.objects.get(id=team_id_))
        
        self.gameinstance_set.add(GameInstance.objects.get(id=new_game_instance.id))
    def getGameInstances(self):
        return GameInstance.objects.select_related("competition").all().order_by('time_taken')
    def __unicode__(self):
        return self.name

class GameInstance(models.Model):
    '''
    TimeModel.objects.create(time=td.total_seconds())
    td = timedelta(seconds=TimeModel.objects.get(id=1).time)
    '''
    competition = models.ForeignKey('Competition')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    pause_time = models.FloatField()
    total_time = timedelta.fields.TimedeltaField(blank=True, null=True)
    time_taken = models.DateTimeField(blank=True, null=True)
    current_question = models.IntegerField()
    started = models.BooleanField()
    paused = models.BooleanField()
    ended = models.BooleanField()
    __pauseStartTime = datetime
    def startClock(self):
        self.start_time = datetime.now()
        ended = false
    def stopClock(self):
        self.end_time = datetime.now()
        self.total_time = self.end_time - self.start_time - self.pause_time
        ended = true
    def pauseClock(self):
        self.paused = true
        self.__pauseStartTime = datetime.now()
    def unpauseClock(self):
        self.paused = false
        self.pause_time += datetime.now() - self.__pauseStartTime
    def getGameTime(self):
        if ended == true:
            return self.total_time
        elif paused == true:
            return self.__pauseStartTime - self.start_time - self.pause_time
        else:
            return datetime.now() - self.start_time - self.pause_time
    def addTeam(self, team_id_):
        self.team_set.add(Team.objects.get(id=team_id_))
    def removeTeam(self, team_id_):
        t = Team.objects.get(id=team_id_)
        t.removeForeignKey()

    #function makes no sense, should be the other way around
    def getTotalTime(self):
        start_game_stage = GameStage.objects.filter(gameinstance=self.id).earliest("id")
        end_game_stage = GameStage.objects.filter(gameinstance=self.id).latest("id")
        return end_game_stage.start_time - start_game_stage.start_time

    def setCurrentQuestion(self, question_number_):
        self.current_question = question_number_
    def getQuest(self):
        return Competition.objects.select_related("gameinstance").filter(id=self.id)
    def getTeam(self):
        return Team.objects.select_related("gameinstance").all()[0]
    def createGameStage(self):
        new_game_stage_instance = GameStage(gameinstance = self, stage = self.current_question) 
        new_game_stage_instance.save() 
        self.gamestage_set.add(GameStage.objects.get(id=new_game_stage_instance.id))      
    def __unicode__(self):
        return u"%s" % self.id

class GameStage(models.Model):
    gameinstance = models.ForeignKey('GameInstance')
    stage = models.IntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    Penalty = models.IntegerField(default=0)
    def __unicode__(self):
        return str(self.stage) + " - " + str(self.start_time)

class Team(models.Model):
    gameinstance = models.ForeignKey('GameInstance', blank=True, null=True)
    name = models.CharField(max_length=32)
    captain_name = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=12)
    email = models.EmailField(null=True, blank=True)
    def removeForeignKey(self):
        self.game_instance = None
        self.save()
    def addPlayer(self, phone_number_, name_, email_):
        plyr = Player(first_name = name_, phone_number = phone_number_, email = email_)
        plyr.save()
        self.player_set.add(Player.objects.get(id=plyr.id))
    def removePlayer(self, player_id_):
        p = Player.objects.get(id=player_id_)
        p.removeForeignKey()       
    def getPlayers(self):
        return Player.objects.select_related("team").filter(id=self.id)
    def __unicode__(self):
        return self.name

class Player(models.Model):
    team = models.ForeignKey('Team', blank=True, null=True)
    phone_number = models.CharField(max_length=12)
    name = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    def removeForeignKey(self):
        self.team = None
        self.save()
    def __unicode__(self):
        return self.phone_number

class QuestionsSolutionPair(models.Model):
    competition = models.ForeignKey('Competition')
    question_number = models.IntegerField()
    question_text = models.CharField(max_length=140)
    is_pause = models.BooleanField(default=False)
    def addSolution(self, solution_):
        sol = Solution(solution_text = solution_)
        sol.save()
    def modifySolution(self, id_, solution_):
        s = Solution.objects.get(id=id_)
        s.setSolution(solution_)
    def removeSolution(self, id_):
        Solution.objects.get(id=id_)
    def getSolutions(self):
        return Solution.objects.select_related("questions_solution_pair").filter(id=self.id)
    def __unicode__(self):
        return self.question_text

class Solution(models.Model):
    questions_solution_pair = models.ForeignKey('QuestionsSolutionPair')
    solution_text = models.CharField(max_length=32)
    def __unicode__(self):
        return self.solution_text
