from django.forms import ModelForm
from django import forms
from quests.models import Team, Player, GameInstance
from promotions.models import PromoCode
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, BaseInlineFormSet

class TeamForm(ModelForm):
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
                    if t.has_paid == True:
                        raise forms.ValidationError('Sorry, this number is already participating in an active game. Please log in for more control over this quest')
                    else:
                        raise forms.ValidationError('Sorry, you have registered a team for a quest with this number but have not yet paid. Please follow this link to either cancel or pay for the quest') 
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

PlayerFormset = inlineformset_factory(Team, Player,  extra=1)

class BaseTeamFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseTeamFormset, self).add_fields(form, index)

        # created the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)

        # store the formset in the .nested property
        form.nested = [
            PlayerFormset(data=self.data,
                            instance = instance,
                            prefix = 'PLAYERS_%s' % pk_value)]

TeamFormset = inlineformset_factory(Team, Player, formset=BaseTeamFormset, extra=1)

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