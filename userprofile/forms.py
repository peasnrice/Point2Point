from django import forms
from models import UserProfile, ProfilePhoneNumber
from phonenumber_field.modelfields import PhoneNumberField


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email_alerts',]
        labels = {'email_alerts': ('I want to receive email alerts'),}


#Commented out until "This Field Cannot be null" is figured out"

class GetPinForm(forms.Form):

    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', 
                                error_message = ("Phone number must include country code '+x-xxx-xxx-xxxx'."), 
                                max_length=15,
                                label=u'Phone Number')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(GetPinForm, self).__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if self.user:
            phone_numbers = ProfilePhoneNumber.objects.filter(user_profile=self.user.profile).filter(phone_number=phone_number)
            if phone_numbers:
                raise forms.ValidationError('You have already registered this number')
            else:
                return phone_number
        else:
            raise forms.ValidationError('Not sure how you managed this, but you aren\'t logged in. Please log in')

class VerifyPinForm(forms.Form):
    pin = forms.CharField(max_length=10)


