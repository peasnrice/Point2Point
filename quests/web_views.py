from Point2Point.settings import *
from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext, HttpResponseRedirect
from django.http import Http404
from quests.models import Competition, Team, Player, GameInstance
#from quests.utils import *
from quests.forms import PlayerForm, TeamForm
from django.forms.models import modelformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.rest import TwilioRestClient
from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from quests.sms_handling import game_logic
import datetime
from django.utils.timezone import utc

import logging
logger = logging.getLogger(__name__)

# Returns Home Page from url /quests/
def quests(request):
    competitions = Competition.objects.all()
    competition_list = []
    expired_list = []
    for competition in competitions:
        current_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        if current_date > competition.start_date and current_date < competition.end_date:
            competition_list.append(competition)
        else:
            expired_list.append(competition)

    return render_to_response('quests/quests.html', locals(), context_instance=RequestContext(request)) 

# Displays form page that allows teams to sign up
# upon signing up twilio sends the user an sms message
def detail(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    current_date = datetime.datetime.utcnow().replace(tzinfo=utc)
    if current_date < competition.start_date or current_date > competition.end_date:
        return render_to_response('quests/sorry.html', locals(), context_instance=RequestContext(request)) 

    form_t = TeamForm(request.POST or None)
    if form_t.is_valid():
        save_team = form_t.save(commit=False)
        save_team.save()
        competition.createGameInstance(save_team.id)
        competition.save()
        team = Team.objects.get(id=save_team.id)
        game = team.gameinstance
        question = game.current_question
        sms_text = competition.getQSPairTextByQNum(question)
        game.createGameStage()      
        client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                                  TWILIO_AUTH_TOKEN)
        message = client.messages.create(body=sms_text,
            to=save_team.phone_number,
            from_="+14385001559")
        return HttpResponseRedirect('/')
    return render_to_response('quests/detail.html', locals(), context_instance=RequestContext(request)) 
 
 # simple class for storing data that is sent to html to be read by rails
class LeaderboardGameData:
    def __init__(self, competition_number_, position_, name_, time_bp_, time_ap_, average_time_):
        self.competition = competition_number_
        self.position = str(position_)
        self.name = name_
        self.time_bp = time_bp_
        self.time_ap = time_ap_
        self.average_time = average_time_  

# returns a list of leaderboardgamedata objects and displays the leaderboard page
def leaderboards(request):
    competition_list = []
    ended_game_list = []
    ongoing_game_list = []
    dnf_game_list = []
    competitions_list = Competition.objects.all()
    number_of_competitions = len(competition_list)
    competition_number = 0
    for competition in competitions_list:
        position = 0
        competition_list.append(competition.name)
        
        game_instances = GameInstance.objects.filter(competition=competition.id).order_by("game_time")
        ended_games = game_instances.filter(ended=True).filter(dnf=False)
        ongoing_games = game_instances.filter(ended=False)
        dnf_games = game_instances.filter(dnf=True)
        
        for ended_game in ended_games:
            position += 1
            team_name = ended_game.getTeamName()
            time_bp = ended_game.game_time
            time_ap = ended_game.total_time
            average_time = ended_game.average_time
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time)
            ended_game_list.append(l)

        for ongoing_game in ongoing_games:
            position = "in progress"
            team_name = ongoing_game.getTeamName()
            time_bp = ongoing_game.game_time
            time_ap = ongoing_game.total_time
            average_time = ongoing_game.average_time
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time)
            ongoing_game_list.append(l)  

        for dnf_game in dnf_games:
            position = "dnf"
            team_name = dnf_game.getTeamName()
            time_bp = dnf_game.game_time
            time_ap = dnf_game.total_time
            average_time = dnf_game.average_time
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time)
            dnf_game_list.append(l)     
            
        competition_number += 1
    context = {'competition_list': competition_list}
    return render_to_response('quests/leaderboards.html', locals(), context_instance=RequestContext(request))   


# When the user replies to a question the response is checked here
@twilio_view
def verify_sms(request):
    from_number = request.POST.get('From', None)  
    from_text = request.POST.get('Body', None)  
    msg = game_logic(from_number, from_text)
    r = Response()
    r.message(msg)
    return r