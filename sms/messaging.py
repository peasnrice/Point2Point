from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER
from twilio.rest import TwilioRestClient

def send_msg(to_number, text):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
 
    message = client.messages.create(to=to_number, from_=TWILIO_NUMBER,
                                     body=text)
