from Point2Point import settings
from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from quests.models import Competition, Team, Player, GameInstance
#from quests.utils import *
from quests.forms import PlayerForm, TeamForm
from django.forms.models import modelformset_factory
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time
from django.utils.timezone import utc
from pytz import timezone
import pytz

from django.http import HttpResponse
from twilio.rest import TwilioRestClient

# Returns Home Page from url /quests/
def index(request):
    competition_list = Competition.objects.all()
    context = {'competition_list': competition_list}
    return render(request, 'quests/index.html', context)

# Twilio authentication details
TWILIO_ACCOUNT_SID = 'AC2b2b2a49dce0a86ed02c04e65e7dbe4e'
TWILIO_AUTH_TOKEN = 'be50c089508b4af31a136bdf6a662f7c'

#Returns signup page and handles sending welcome text message
def detail(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    form_t = TeamForm(request.POST or None)

    if form_t.is_valid():
        save_team = form_t.save(commit=False)
        save_team.save()

        competition = Competition.objects.get(id=competition_id)
        competition.createGameInstance(save_team.id)
        competition.save()

        team = Team.objects.get(id=save_team.id)
        game = team.gameinstance
        question = game.current_question

        sms_text = competition.getQSPairTextByQNum(question)

        sms_text = sms_text.replace("<TEAM>", save_team.name)
        sms_text = sms_text.replace("<CAPTAIN>", save_team.captain_name)        

        client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                                  TWILIO_AUTH_TOKEN)

        message = client.messages.create(body=sms_text,
            to=save_team.phone_number,
            from_="+14385001559")


    return render_to_response('quests/detail.html', locals(), context_instance=RequestContext(request)) 
 
def leaderboards(request):
    competition_list = Competition.objects.all()
    context = {'competition_list': competition_list}
    return render(request, 'quests/leaderboards.html', context)

class LeaderboardData:
    def __init__(self, position_, name_, time_):
        self.position = position_
        self.name = name_
        self.time = time_


def leaderboard_detail(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    competition = Competition.objects.get(id=competition_id)
    games = competition.getGameInstances()
    position = 1
    not_started = []
    in_progress = []
    ended = []
    for game in games:
        if game.started == True and game.ended == True:
            l = LeaderboardData(position, game.getTeam().name, game.time_taken)
            ended.append(l)
            position += 1
        elif game.started == True:
            l = LeaderboardData(999, game.getTeam().name, game.time_taken)
            in_progress.append(l)
        else:
            l = LeaderboardData(999, game.getTeam().name, game.time_taken)
            not_started.append(l)           
    return render_to_response('quests/leaderboard_detail.html', locals(), context_instance=RequestContext(request)) 

def registered(request, team_id):

    team = Team.objects.get(id=team_id)
    players = team.getPlayers()

    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)

    message = client.messages.create(body="Welcome" + players[0].first_name + "!, to begin reply to this number with, start",
        to=players[0].phone_number,
        from_="+14385001559")

    return render_to_response('quests/detail.html', locals(), context_instance=RequestContext(request)) 

@twilio_view
def verify_sms(request):
    from_text = request.REQUEST.get('Body', None)    
    r = Response()
    r.message(from_text.lower())
    return r

# When the user replies to a question the response is checked here
@csrf_exempt
def verify_sms(request):
    """Respond to incoming calls with a simple text message."""
      
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)

    # retrieve phone number
    from_number = request.REQUEST.get('From', None)
    # find all teams belonging to number
    teams = Team.objects.filter(phone_number=from_number)
    # if no teams exist, tell user to register otherwise 
    if not teams:
        reply_text = "Sorry, you aren't registered in an active Quest, register at www.PointToPoint.com"
    else:
        has_active_game = False
        active_team = Team()
        for team in teams:
            if team.gameinstance.ended == False:
                has_active_game = True
                active_team = team
                break
        if has_active_game == True:
            game = active_team.gameinstance
            solutions = game.competition.getSolutions(game.current_question)
            from_text = request.REQUEST.get('Body', None).lower()
            
            break_flag = False
            for solution in solutions:
                if from_text == solution.solution_text.lower():
                    if game.current_question == 0:
                        game.started = True
                        montreal = timezone('America/Montreal')
                        game.start_time = datetime.utcnow().replace(tzinfo=montreal)
                        game.save()
                    game.current_question += 1
                    game.save()
                    if game.current_question >= game.competition.getQuestLength():
                        game.started = True
                        game.ended = True
                        montreal = timezone('America/Montreal')
                        game.end_time = datetime.utcnow().replace(tzinfo=montreal)
                        dt = game.getTimeDelta()
                        game.time_taken = dt
                        game.save()
                        reply_text = "Congratulations you have finished the quest in " + str(dt) + "!"
                    else:
                        reply_text = game.competition.getQuestion(game.current_question)
                    break_flag = True
            if break_flag == False:
                reply_text = "sorry, " + from_text + " is not a valid input, please try again." 
        else:
            reply_text = "Sorry, you don't appear to be participating in an active game"          
    
    message = client.messages.create(body=reply_text,
        to=from_number,
        from_="+14385001559")
    print message.sid

@csrf_exempt
def echo(request):
    """Respond to incoming calls with a simple text message."""
      
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)

    from_number = request.REQUEST.get('From', None)
    from_text = request.REQUEST.get('Body', None)
    message = client.messages.create(body=from_text,
        to=from_number,
        from_="+14385001559")

    print message.sid


def mysms(request):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)

    message = client.messages.create(body="Hello!",
        to="+15149240757",
        from_="+14385001559")

    print message.sid
