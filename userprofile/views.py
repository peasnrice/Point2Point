from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from twilio.rest import TwilioRestClient
from forms import UserProfileForm, GetPinForm, VerifyPinForm
from django.contrib.auth.decorators import login_required
from phonenumber_field.modelfields import PhoneNumberField
from quests.models import Team
from models import ProfilePhoneNumber
import phonenumbers
import string
import random

@login_required
def user_profile(request):

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/login')
    else:
        user = request.user
        profile = user.profile
        verified_numbers = ProfilePhoneNumber.objects.filter(user_profile=profile)
        verified_number_list = []
        for number in verified_numbers:
            num = "+" + str(number.phone_number.country_code) + str(number.phone_number.national_number)
            verified_number_list.append(num)
        form = UserProfileForm(instance=profile)
    return render_to_response('userprofile/profile.html', locals(), context_instance=RequestContext(request))

def pin_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def send_msg(to_number, text):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
 
    message = client.messages.create(to=to_number, from_=TWILIO_NUMBER,
                                     body=text)

@login_required
def get_pin(request):
    get_pin_form = GetPinForm(request.POST or None)
    if get_pin_form.is_valid():
        pin = pin_generator()
        number = get_pin_form.cleaned_data['phone_number']
        phone_number = "+" + str(number.country_code) + str(number.national_number)
        send_msg(phone_number,pin)
        request.session['pin'] = pin
        request.session['phone_number'] = phone_number
        return HttpResponseRedirect('/profile/verifypin')
    return render_to_response('userprofile/get_pin.html', locals(), context_instance=RequestContext(request))

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
    return render_to_response('userprofile/verify_pin.html', locals(), context_instance=RequestContext(request))

def _get_pin(length=5):
    """ Return a numeric PIN with length digits """
    return random.sample(range(10**(length-1), 10**length), 1)[0]


def _verify_pin(mobile_number, pin):
    """ Verify a PIN is correct """
    return pin == cache.get(mobile_number)


def ajax_send_pin(request):
    """ Sends SMS PIN to the specified number """
    mobile_number = request.POST.get('mobile_number', "")
    if not mobile_number:
        return HttpResponse("No mobile number", mimetype='text/plain', status=403)

    pin = _get_pin()

    # store the PIN in the cache for later verification.
    cache.set(mobile_number, pin, 24*3600) # valid for 24 hrs

    client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
                        body="%s" % pin,
                        to=mobile_number,
                        from_=settings.TWILIO_FROM_NUMBER,
                    )
    return HttpResponse("Message %s sent" % message.sid, mimetype='text/plain', status=200)

def process_order(request):
    """ Process orders made via web form and verified by SMS PIN. """
    form = OrderForm(request.POST or None)

    if form.is_valid():
        pin = int(request.POST.get("pin", "0"))
        mobile_number = request.POST.get("mobile_number", "")

        if _verify_pin(mobile_number, pin):
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