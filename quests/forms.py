from django.forms import ModelForm
from quests.models import Team, Player

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'captain_name', 'phone_number', 'email']
        labels = {'name': ('Team Name'),
        }

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'phone_number', 'email']
