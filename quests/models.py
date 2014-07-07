from Point2Point import settings
from django.db import models
from django.utils.timezone import utc
from django.forms import ModelForm
from django.db.models import Count
from django.db import models
from django.template.defaultfilters import slugify
import timedelta, datetime
from django.utils.timezone import utc

class Competition(models.Model):
    quest_type = models.ForeignKey('QuestType')
    name = models.CharField(max_length=512)
    slug = models.SlugField(default="will-change-on-save")
    start_destination = models.CharField(max_length=512)
    description = models.TextField()
    price = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    greeting = models.CharField(max_length=512)
    congratulation = models.CharField(max_length=512)
    estimated_duration = models.IntegerField()
    team_size_limit = models.IntegerField()
    creators_name = models.CharField(max_length=32)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    start_time_latest = models.TimeField()
    start_time_earliest = models.TimeField()
    end_time = models.TimeField()
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
                     started = False, ended = False, paused = True, total_time=datetime.timedelta(seconds=0),
                        average_time=datetime.timedelta(seconds=0),penalty_time=datetime.timedelta(seconds=0),
                            game_time=datetime.timedelta(seconds=0)) 
        new_game_instance.save()
        new_game_instance.team_set.add(Team.objects.get(id=team_id_))
        self.gameinstance_set.add(GameInstance.objects.get(id=new_game_instance.id))
        return new_game_instance
    def getGameInstances(self):
        return GameInstance.objects.filter(competition=self.id)
    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)
        super(Competition, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.name

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

class GameInstance(models.Model):
    competition = models.ForeignKey('Competition')
    date_created = models.DateTimeField(auto_now_add=True)
    date_started = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=utc), blank=True)

    total_time = timedelta.fields.TimedeltaField(blank=True)
    game_time = timedelta.fields.TimedeltaField(blank=True)
    penalty_time = timedelta.fields.TimedeltaField(blank=True)
    average_time = timedelta.fields.TimedeltaField(blank=True)
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
    paused = models.BooleanField(default=False)
    dnf = models.BooleanField(default=False)



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
        
        time_delta = datetime.timedelta(0)
        if self.started == True and self.ended == False and self.paused == False:
            gs = GameStage.objects.filter(gameinstance=self.id).latest('time_stamp')
            time_delta = (datetime.datetime.utcnow().replace(tzinfo=utc) - gs.time_stamp) + self.game_time
        else:
            time_delta = self.game_time


        average_time = strfdelta(self.average_time, "{hours}h {minutes}m {seconds}s")
        game_time = strfdelta(time_delta, "{hours}h {minutes}m {seconds}s")
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
    has_paid = models.BooleanField(default=False)
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
    question_text = models.TextField()
    clue_hint_text = models.TextField()
    location_hint_text = models.TextField()
    is_pause = models.BooleanField(default=False)
    pause_duration = timedelta.fields.TimedeltaField(blank=True, null=True)
    def __unicode__(self):
        return "COMP: " + str(self.competition.name) + " - Q#: " + str(self.question_number)

class Solution(models.Model):
    questions_solution_pair = models.ForeignKey('QuestionsSolutionPair')
    solution_text = models.CharField(max_length=64)
    def __unicode__(self):
        return self.solution_text

class QuestType(models.Model):
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=32)
    caption = models.CharField(max_length=64)
    description = models.TextField()
    who_is_it_for = models.TextField()
    what_it_is = models.TextField()
    how_it_works = models.TextField()
    other_details = models.TextField()
    front_page = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name