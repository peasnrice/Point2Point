from django import forms
from models import UserProfile, ProfilePhoneNumber

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['email_alerts',]
		labels = {'email_alerts': ('I want to receive email alerts'),}

class GetPinForm(forms.ModelForm):
	class Meta:
		model = ProfilePhoneNumber
		fields = ['phone_number',]
		labels = {'phone_number': ('Phone Number'),}

class VerifyPinForm(forms.Form):
	pin = forms.CharField(max_length=10)
