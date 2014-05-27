from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER
from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext, HttpResponseRedirect
from django.http import Http404
from django.core.mail import send_mail
from quests.models import Competition, Team, Player, GameInstance
from quests.forms import PlayerForm, TeamForm
from django.forms.models import modelformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.rest import TwilioRestClient
from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from quests.sms_handling import game_logic
from django.utils.timezone import utc
import datetime

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

        subject = competition.name
        from_email = 'PointToPoint@pointtopoint.webfactional.com'
        body = "Congratulations team "
        body += team.name
        body += " on signing up for the "
        body += competition.name 
        body += " Point To Point quest!\n\n"
        body += "You should have received a confirmation message on your captains phone number or if not it should arrive shortly!\n"
        body += "You can start the quest whenever you like, just make sure you start it within the allowed time boundries of the quest. "
        body += "Every quest has different time restrictions!\n\n" 
        body += "there are several key words you can use to help you along your way, these are:\n"
        body += "\"game help\" - displays these commands on your phone\n"
        body += "\"repeat\" - repeats the current riddle, clue or question\n"
        body += "\"game info\" - displays you various information regarding your progress\n"
        body += "\"location hint\" - Gives you a clue on where you need to be, the first location hint is free an additional location hint will be a 10 minute penalty\n"
        body += "\"clue hint\" - Gives you a clue to solve the riddel, the first clue hint is free an additional clue hint will be a 10 minute penalty\n"
        body += "\"skip\" - Skips the current question but adds a 30 minute penalty, only to be used when you really can't figure it out!\n"
        body += "\"game quit\" - quits your current quest, there is no undoing this! YOU HAVE BEEN WARNED\n"
        body += "\nJust in case you lose the phone number here it is again: "
        body += TWILIO_NUMBER
        body += "If you have any question along your way please contact support at andy@pointtopoint.webfactional.com "
        body += "and we will get back to you as quickly as possible\n\n"
        body += "\n\nHappy questing team "
        body += team.name
        body += "!"
        to_email = team.email
        send_mail(subject, body, from_email,[to_email], fail_silently=False)
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