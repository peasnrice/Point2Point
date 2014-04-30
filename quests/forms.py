from django.forms import ModelForm
from django import forms
from quests.models import Team, Player, GameInstance
from promotions.models import PromoCode

class TeamForm(ModelForm):
    #beta_access_code = forms.CharField()
    class Meta:
        model = Team
        fields = ['name', 'captain_name', 'phone_number', 'email']
        labels = {'name': ('Team Name'),
        }
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

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'phone_number', 'email']