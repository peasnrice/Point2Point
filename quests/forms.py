from django.forms import ModelForm
from django import forms
from quests.models import Team, Player, GameInstance

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
                    raise forms.ValidationError('Sorry, this number is already participating in an active game')
        return phone_number

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'phone_number', 'email']
