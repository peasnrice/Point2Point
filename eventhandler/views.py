from django.http import HttpResponse
from eventhandler.tasks import resumeGame
from twilio.rest import TwilioRestClient

def test_async(request):
	add_to_count.apply_async(countdown=10)
	string = str(SampleCount.objects.all()[0].num)
	return HttpResponse(string)

def send_msg(to_number, text):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
 
    message = client.messages.create(to=to_number, from_="+14385001559",
                                     body=text)

