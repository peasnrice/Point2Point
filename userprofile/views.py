from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER
from django.shortcuts import render_to_response, RequestContext, HttpResponse, render
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from twilio.rest import TwilioRestClient
from forms import UserProfileForm, GetPinForm, VerifyPinForm
from django.contrib.auth.decorators import login_required
from phonenumber_field.modelfields import PhoneNumberField
from quests.models import Team, GameInstance
from models import ProfilePhoneNumber
import phonenumbers
import string
import random
import json
from django.utils import simplejson
from django.core import serializers

@login_required
def ajax(request):

    name = request.GET['name']
    user = request.user
    profile = user.profile

    #data = serializers.serialize("json", ProfilePhoneNumber.objects.all())

    data = serializers.serialize('json', [ user, ])

    return_dict = {
        'name': name,
        'user': data
    }
    json = simplejson.dumps(return_dict)
    return HttpResponse(json, mimetype="application/x-javascript")

    #return render_to_response('userprofile/ajax.html', locals(), context_instance=RequestContext(request))

@login_required
def user_profile(request):
    if request.method == 'POST':
        form = GetPinForm(request.POST)
        if form.is_valid():
            if request.is_ajax():
                errors_dict = {}
                if form.errors:
                    for error in form.errors:
                        e = form.errors[error]
                        errors_dict[error] = unicode(e)
                return HttpResponseBadRequest(json.dumps(errors_dict))
            else:
                pass
    else:
        user = request.user
        profile = user.profile

        in_progress_list = []
        completed_list = []
        games = profile.game_instances.all()
        for game in games:
            if game.ended:
                completed_list.append(game)
            else:
                in_progress_list.append(game)
        verified_numbers = ProfilePhoneNumber.objects.filter(user_profile=profile)
        verified_number_list = []
        for number in verified_numbers:
            num = "+" + str(number.phone_number.country_code) + str(number.phone_number.national_number)
            verified_number_list.append(num)
        form = GetPinForm()

    args = {}
    args['in_progress_list'] = in_progress_list
    args['completed_list'] = completed_list
    args['verified_number_list'] = verified_number_list
    args['form'] = form
    args['username'] = user.username
    args['phone_number_verified'] = user.profile.phone_number_verified
    args['verified_number_list'] = verified_number_list

    return render_to_response('userprofile/profile.html', args, context_instance=RequestContext(request))

'''
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        get_pin_form = GetPinForm(user=request.user, data=request.POST)
        verify_pin_form = VerifyPinForm(request.POST or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/login')
        elif get_pin_form.is_valid():
            pin = pin_generator()
            number = get_pin_form.cleaned_data['phone_number']
            phone_number = "+" + str(number.country_code) + str(number.national_number)
            send_msg(phone_number,pin)
            request.session['pin'] = pin
            request.session['phone_number'] = phone_number
            #return HttpResponseRedirect('#')
        elif verify_pin_form.is_valid():
            pin = request.session['pin']
            if pin == verify_pin_form.cleaned_data['pin']:
                user = request.user
                profile = user.profile

                phone_number = request.session['phone_number']
                new_verified_phone_number = ProfilePhoneNumber(user_profile=profile,phone_number=phone_number)
                new_verified_phone_number.save()

                profile.phone_number_verified = True
                profile.save()

                teams = Team.objects.filter(phone_number=phone_number)
                for team in teams:
                    profile.game_instances.add(team.gameinstance)
                    profile.save()
                #return HttpResponseRedirect('#')
    else:
        user = request.user
        profile = user.profile

        in_progress_list = []
        completed_list = []
        games = profile.game_instances.all()
        for game in games:
            if game.ended:
                completed_list.append(game)
            else:
                in_progress_list.append(game)
        verified_numbers = ProfilePhoneNumber.objects.filter(user_profile=profile)
        verified_number_list = []
        for number in verified_numbers:
            num = "+" + str(number.phone_number.country_code) + str(number.phone_number.national_number)
            verified_number_list.append(num)
        form = UserProfileForm(instance=profile)
        get_pin_form = GetPinForm(user=request.user)
        verify_pin_form = VerifyPinForm()
    return render_to_response('userprofile/profile.html', locals(), context_instance=RequestContext(request))
'''

def pin_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def send_msg(to_number, text):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
 
    message = client.messages.create(to=to_number, from_=TWILIO_NUMBER,
                                     body=text)

@login_required
def get_pin(request):
    if request.method == 'POST':
        get_pin_form = GetPinForm(data=request.POST)
        if get_pin_form.is_valid():
            pin = pin_generator()
            number = get_pin_form.cleaned_data['phone_number']
            phone_number = "+" + str(number.country_code) + str(number.national_number)
            send_msg(phone_number,pin)
            request.session['pin'] = pin
            request.session['phone_number'] = phone_number
            return HttpResponseRedirect('/profile/verifypin')
    else:
        get_pin_form = GetPinForm()

    args = {}
    args['get_pin_form'] = get_pin_form
    return render_to_response('userprofile/get_pin.html', args, context_instance=RequestContext(request))

@login_required
def verify_pin(request):
    verify_pin_form = VerifyPinForm(request.POST or None)
    if verify_pin_form.is_valid():
        pin = request.session['pin']
        if pin == verify_pin_form.cleaned_data['pin']:
            user = request.user
            profile = user.profile

            phone_number = request.session['phone_number']
            new_verified_phone_number = ProfilePhoneNumber(user_profile=profile,phone_number=phone_number)
            new_verified_phone_number.save()

            profile.phone_number_verified = True
            profile.save()

            teams = Team.objects.filter(phone_number=phone_number)
            for team in teams:
                profile.game_instances.add(team.gameinstance)
                profile.save()
            return HttpResponseRedirect('/profile')
        else:
            return HttpResponseRedirect('/profile/verifypin')
    args = {}
    args['verify_pin_form'] = verify_pin_form
    return render_to_response('userprofile/verify_pin.html', args, context_instance=RequestContext(request))

def _get_pin(length=5):
    """ Return a numeric PIN with length digits """
    return random.sample(range(10**(length-1), 10**length), 1)[0]


def _verify_pin(phone_number, pin):
    """ Verify a PIN is correct """
    return pin == cache.get(phone_number)

@csrf_protect
def ajax_send_pin(request):
    """ Sends SMS PIN to the specified number """
    phone_number = request.POST.get('phone_number', "")
    if not phone_number:
        return HttpResponse("No mobile number", mimetype='text/plain', status=403)

    pin = _get_pin()

    # store the PIN in the cache for later verification.
    cache.set(phone_number, pin, 24*3600) # valid for 24 hrs

    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
                        body="%s" % pin,
                        to=phone_number,
                        from_=TWILIO_NUMBER,
                    )
    return HttpResponse("Message %s sent" % message.sid, mimetype='text/plain', status=200)

def process_order(request):
    """ Process orders made via web form and verified by SMS PIN. """
    form = OrderForm(request.POST or None)

    if form.is_valid():
        pin = int(request.POST.get("pin", "0"))
        phone_number = request.POST.get("phone_number", "")

        if _verify_pin(phone_number, pin):
            form.save()
            return redirect('transaction_complete')
        else:
            messages.error(request, "Invalid PIN!")
    else:
        return render(
                    request,
                    'order.html',
                    {
                        'form': form
                    }
                )