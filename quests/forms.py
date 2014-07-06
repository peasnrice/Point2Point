from django.forms import ModelForm
from django import forms
from quests.models import Team, Player, GameInstance
from promotions.models import PromoCode
from django.contrib.auth.models import User

class TeamForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TeamForm, self).__init__(*args, **kwargs)
    #beta_access_code = forms.CharField()
    class Meta:
        stripe_id = forms.CharField(max_length=255)
        model = Team
        fields = ['name', 'captain_name', 'phone_number', 'email']
        labels = {'name': ('Team Name'),
        }

    def add_error(self, message):
        self.errors[NON_FIELD_ERRORS] = self.error_class([message])

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        ts = Team.objects.filter(phone_number=phone_number)        
        if ts:
            for t in ts:
                if t.gameinstance.ended == False:
                    raise forms.ValidationError('Sorry, this number is already participating in an active game')
        
        #Check for trusted phone numbers in promo code list
        trusted_numbers = PromoCode.objects.filter(valid=True)
        number_found = False
        if not trusted_numbers:
            raise forms.ValidationError('Sorry this number is not part of the beta trial')
        else:
            for number in trusted_numbers:
                if number.code == phone_number:
                    return phone_number
            raise forms.ValidationError('Sorry this number is not part of the beta trial')
   
    def clean_beta_access_code(self):
        promo_code = self.cleaned_data['beta_access_code']
        pcs = PromoCode.objects.filter(valid=True)
        promo_found = False
        if not pcs:
            raise forms.ValidationError("Sorry you can't use this code at this time")
        else:
            for pc in pcs:
                if pc.code == promo_code:
                    promo_found = True
                    break
            if promo_found:
                #pc.valid = False
                #pc.delete()
                return promo_code  
            else:
                raise forms.ValidationError("Sorry you can't use this code at this time")


class LoggedInTeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name',]
        labels = {'name': ('Team Name'),
        }        

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'phone_number', 'email']