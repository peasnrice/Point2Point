from django.forms import ModelForm
from django import forms
from quests.models import Team, Player, GameInstance, Competition
from promotions.models import PromoCode
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory, BaseInlineFormSet

class TeamForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop('competition', None)
        super(TeamForm, self).__init__(*args, **kwargs)
            
    class Meta:
        model = Team
        fields = ['name', 'captain_name', 'phone_number', 'email']
        labels = {'name': ('Team Name'),
        }

    
    def clean_phone_number(self):
        print self.competition
        phone_number = self.cleaned_data['phone_number']
        ts = Team.objects.filter(phone_number=phone_number)
        if ts:
            for t in ts:
                if t.gameinstance.ended == False:
                    if t.has_paid == True:
                        raise forms.ValidationError('Sorry, this number is already participating in an active game. Please log in for more control over this quest')
                    else:
                        raise forms.ValidationError('Sorry, you\'ve registered but haven\'t paid yet. To return to the payment page, please check your email for your unique payment url') 
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
    
    '''
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
    '''

class BaseTeamFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.competition = kwargs.pop('competition', None)
        super(BaseTeamFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

    def clean(self):
        """Checks that no two phone numbers or team names are the same."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        team_names = []
        numbers = []
        for form in self.forms:
            team_name = form.cleaned_data['name']
            number = form.cleaned_data['phone_number']
            if team_name in team_names:
                raise forms.ValidationError("Team names must be unique")
            if number in numbers:
                raise forms.ValidationError("Phone numbers must be unique")
            team_names.append(team_name)
            numbers.append(number)

            if self.competition:
                teams = Team.objects.filter(competition=self.competition)
                for team in teams:
                    if team.name == team_name:
                        raise forms.ValidationError('Sorry, a team with the name \'' + team_name + '\' already exists in this competition. Please choose another name')
                    else:
                        return team_name
            else:
                raise forms.ValidationError('You must be registering for a valid competition')
