from twilio.twiml import Response
from django_twilio.decorators import twilio_view

@twilio_view
def verify_sms(request):
    from_text = request.REQUEST.get('Body', None)    
    r = Response()
    r.message(from_text.lower())
    return r