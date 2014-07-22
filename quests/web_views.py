from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER, STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext, HttpResponseRedirect
from django.http import Http404
from django.core.mail import send_mail
from quests.models import Competition, Team, Player, GameInstance, QuestType
from userprofile.models import ProfilePhoneNumber
from quests.forms import PlayerForm, TeamForm, TeamFormset
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.rest import TwilioRestClient
from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from quests.sms_handling import game_logic
from django.utils.timezone import utc
from payment import urls
import datetime
import stripe
from django.forms.formsets import formset_factory, BaseFormSet

import logging
logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY

def create_gameinstances_teams(request, quest_type_id, short_name, competition_id, slug):
    """Create one or many game instances consisting of at least 1 team and optional players."""


# Returns Home Page from url /quests/
def quests(request):
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    args = {}
    args['quest_types'] = quest_types
    return render_to_response('quests/quests.html', args, context_instance=RequestContext(request)) 

def quest_list_type(request, quest_type_id, short_name):
    quest_type = get_object_or_404(QuestType, pk=quest_type_id)
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    competitions = Competition.objects.filter(quest_type=quest_type)
    competition_list = []
    expired_list = []
    for competition in competitions:
        current_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        if current_date > competition.start_date and current_date < competition.end_date:
            competition_list.append(competition)
        else:
            expired_list.append(competition)
    args = {}
    args['competition_list'] = competition_list
    args['expired_list'] = expired_list
    args['quest_type'] = quest_type
    args['quest_types'] = quest_types
    return render_to_response('quests/quest_detail.html', args, context_instance=RequestContext(request))  

# Displays form page that allows teams to sign up
# upon signing up twilio sends the user an sms message
def quest_register_team(request, quest_type_id, short_name, competition_id, slug):
    
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
    
    TeamFormSet = formset_factory(TeamForm, formset=RequiredFormSet)

    competition = get_object_or_404(Competition, pk=competition_id)
    current_date = datetime.datetime.utcnow().replace(tzinfo=utc)
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    if current_date < competition.start_date or current_date > competition.end_date:
        args = {}
        args['quest_types'] = quest_types
        return render_to_response('quests/sorry.html', args, context_instance=RequestContext(request)) 

    if request.method == 'POST':
        formset = TeamFormSet(data=request.POST or None)
        form_t = TeamForm(data=request.POST or None)
        if formset.is_valid():
            for form in formset:
                save_team = form.save(commit=False)
                save_team.save()
                competition.createGameInstance(save_team.id)
                competition.save()
                team = Team.objects.get(id=save_team.id)
                request.session['game_id'] = team.gameinstance.id
            return HttpResponseRedirect(reverse('payment success', args=(quest_type_id, short_name, competition_id, slug)))
    else:
        form_t = TeamForm()
        formset = formset_factory(TeamForm)

    args = {}
    args['competition'] = competition
    args['form_t'] = form_t
    args['formset'] = formset
    args['quest_types'] = quest_types
    return render_to_response('quests/register_team.html', args, context_instance=RequestContext(request)) 

# When the user replies to a question the response is checked here
@twilio_view
def verify_sms(request):
    from_number = request.POST.get('From', None)  
    from_text = request.POST.get('Body', None)  
    msg = game_logic(from_number, from_text)
    r = Response()
    r.message(msg)
    return r