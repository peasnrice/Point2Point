class CreditCardForm(forms.Form):

    card_number = forms.CharField(
        label = "Card Number",
        max_length = 80,
        required = True
    )

    cvc = forms.CharField(
        label = "CVC",
        max_length = 3,
        required = True
    )

    class Meta:
        model = UserProfile
        fields = ['email_alerts',]
        labels = {'email_alerts': ('I want to receive email alerts'),}