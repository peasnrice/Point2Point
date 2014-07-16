from dajax.core import Dajax
from dajaxice.utils import deserialize_form
from dajaxice.decorators import dajaxice_register
from sms.messaging import send_msg 
from userprofile.forms import GetPinForm, VerifyPinForm 
from userprofile.models import ProfilePhoneNumber
from quests.models import Team
import string
import random

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
            dajax.clear('.help-block', 'innerHTML')
            dajax.script('modal_be_gone();')
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
    dajax = Dajax()
    user = request.user
    ppn = ProfilePhoneNumber.objects.filter(user_profile=user).filter(phone_number=number)
    ppn.delete()
    
    verified_number_list = ProfilePhoneNumber.objects.filter(user_profile=user)
    render = render_to_string('userprofile/profile.html', {'verified_number_list': verify_number_list})
    
    dajax.assign('#verified_numbers', 'innerHTML', render)
    return dajax.json()
