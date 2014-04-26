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
from twilio.twiml import Response
from django_twilio.decorators import twilio_view

from quests.sms_handling import game_logic

'''
import logging
logger = logging.getLogger(__name__)
'''

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

        game.createGameStage()

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

# When the user replies to a question the response is checked here
@twilio_view
def verify_sms(request):
    from_number = request.POST.get('From', None)  
    from_text = request.POST.get('Body', None)  
    msg = game_logic(from_number, from_text)
    r = Response()
    r.message(msg)
    return r
