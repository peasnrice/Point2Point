from dajax.core import Dajax
from dajaxice.utils import deserialize_form
from dajaxice.decorators import dajaxice_register
from sms.messaging import send_msg 
from userprofile.forms import GetPinForm, VerifyPinForm 
from userprofile.models import ProfilePhoneNumber, UserProfile
from quests.models import Team
import string
import random
from django.template.loader import render_to_string
from userprofile.views import get_phone_numbers

def pin_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@dajaxice_register
def phone_form(request, get_pin_form):
    dajax = Dajax()
    get_pin_form = GetPinForm(user=request.user, data=deserialize_form(get_pin_form))

    if get_pin_form.is_valid():
        dajax.remove_css_class('#phone_number_form input', 'error')
        #pin = pin_generator()
        pin = '1234'
        phone_number = get_pin_form.cleaned_data['phone_number']
        #send_msg(phone_number,pin)
        request.session['pin'] = pin
        request.session['phone_number'] = phone_number
        dajax.clear('.help-block', 'innerHTML')
        dajax.script('go_to_verify();')
    else:
        dajax.remove_css_class('#phone_number_form input', 'error')
        for error in get_pin_form.errors:
            dajax.add_css_class('#id_%s' % error, 'error')
        dajax.assign('.help-block', 'innerHTML',  get_pin_form.errors.values())
    return dajax.json()

@dajaxice_register
def verify_form(request, verify_pin_form):
    dajax = Dajax()
    verify_pin_form = VerifyPinForm(data=deserialize_form(verify_pin_form))
    if verify_pin_form.is_valid():
        dajax.remove_css_class('#phone_number_form input', 'error')
        pin = request.session['pin']
        if pin == verify_pin_form.cleaned_data['pin']:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)

            phone_number = request.session['phone_number']
            phone_number_check = ProfilePhoneNumber.objects.filter(user_profile=user_profile).filter(phone_number=phone_number)

            if not phone_number_check:
                new_verified_phone_number = ProfilePhoneNumber(user_profile=user_profile,phone_number=phone_number)
                new_verified_phone_number.save()

                user_profile.phone_number_verified = True
                user_profile.save()    
                
                teams = Team.objects.filter(phone_number=phone_number)
                for team in teams:
                    user_profile.game_instances.add(team.gameinstance)
                    user_profile.save()
                verified_numbers = ProfilePhoneNumber.objects.filter(user_profile=user_profile)
                verified_number_list = []
                for number in verified_numbers:
                    verified_number_list.append(number.phone_number)
                render = render_to_string('userprofile/numbers_div.html', {'verified_number_list': verified_number_list})
                dajax.assign('#verified_numbers', 'innerHTML', render)
            else:
                dajax.assign('.help-block', 'innerHTML',  'Number Already Registered')
        else:
            dajax.assign('.help-block', 'innerHTML',  'Incorrect Pin')
    else:
        dajax.remove_css_class('#phone_number_form input', 'error')
        for error in verify_pin_form.errors:
            dajax.add_css_class('#id_%s' % error, 'error')
        dajax.assign('.help-block', 'innerHTML',  verify_pin_form.errors.values())

    return dajax.json()

@dajaxice_register
def delete_number(request, number):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    ppn = ProfilePhoneNumber.objects.filter(user_profile=user_profile).filter(phone_number=number)
    ppn.delete()
    verified_numbers = ProfilePhoneNumber.objects.filter(user_profile=user_profile)
    verified_number_list = []
    for number in verified_numbers:
        verified_number_list.append(number.phone_number)
    render = render_to_string('userprofile/numbers_div.html', {'verified_number_list': verified_number_list})
    
    dajax = Dajax()    
    dajax.assign('#verified_numbers', 'innerHTML', render)
    return dajax.json()
