from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER
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
def detail(request, competition_id, slug):
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
            from_=TWILIO_NUMBER)
        return HttpResponseRedirect('/')
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