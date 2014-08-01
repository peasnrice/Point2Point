from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER, STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
from django.shortcuts import render, HttpResponseRedirect, render_to_response, RequestContext, get_object_or_404
from quests.models import Competition, GameInstance, Team, QuestType, GameInstanceConnector
from userprofile.models import ProfilePhoneNumber
from twilio.rest import TwilioRestClient
from django.core.mail import send_mail
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
import stripe

def send_confirmation(game_connector_id):
    game_connector = get_object_or_404(GameInstanceConnector, pk=game_connector_id)
    games = GameInstance.objects.filter(game_instance_connector=game_connector)

    for game in games:
        team = Team.objects.get(gameinstance=game.id)

        game_connector.has_paid = True
        game_connector.save()

        team.has_paid=True
        team.save()

        competition = game.competition
        question = game.current_question
        sms_text = competition.getQSPairTextByQNum(question)
        game.createGameStage()    
        client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                                  TWILIO_AUTH_TOKEN)
        message = client.messages.create(body=sms_text,
            to=team.phone_number,
            from_=TWILIO_NUMBER)

        known_user_numbers = ProfilePhoneNumber.objects.filter(phone_number=team.phone_number)
        for known_user in known_user_numbers:
            known_user.user_profile.game_instances.add(game)
            known_user.user_profile.save()

        subject = competition.name
        from_email = 'andy@p2pquests.com'
        body = "Congratulations team "
        body += team.name
        body += " on signing up for the "
        body += competition.name 
        body += " Point To Point quest!\n\n"
        body += "You should have received a confirmation message on your captains phone number or if not it should arrive shortly!\n"
        body += "You can start the quest whenever you like, just make sure you start it within the allowed time boundries of the quest if there are any. "
        body += "Every quest has different time restrictions!\n\n" 
        body += "there are several key words you can use to help you along your way, these are:\n"
        body += "\"game help\" - displays these commands on your phone\n"
        body += "\"repeat\" - repeats the current riddle, clue or question\n"
        body += "\"game info\" - displays you various information regarding your progress\n"
        body += "\"location hint\" - Gives you a clue on where you need to be, the first location hint is free an additional location hint will be a 10 minute penalty\n"
        body += "\"clue hint\" - Gives you a clue to solve the riddel, the first clue hint is free an additional clue hint will be a 10 minute penalty\n"
        body += "\"skip\" - Skips the current question but adds a 30 minute penalty, only to be used when you really can't figure it out!\n"
        body += "\"game quit\" - quits your current quest, there is no undoing this! YOU HAVE BEEN WARNED\n"
        body += "\nJust in case you lose the phone number here it is again: "
        body += TWILIO_NUMBER
        body += ". If you have any question along your way please contact support at andy@p2pquests.com"
        body += " and we will get back to you as quickly as possible"
        body += "\n\nHappy questing team "
        body += team.name
        body += "!"
        to_email = team.email
        send_mail(subject, body, from_email,[to_email], fail_silently=False)    

def payment(request, quest_type_id, short_name, competition_id, slug, game_connector_id):
    game_connector = get_object_or_404(GameInstanceConnector, pk=game_connector_id)
    competition = get_object_or_404(Competition, pk=competition_id)

    number_of_teams = GameInstance.objects.filter(game_instance_connector = game_connector).count()

    amount = int(competition.price)*number_of_teams
    stripe_amount = amount*100

    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account
    stripe.api_key = STRIPE_SECRET_KEY

    # Get the credit card details submitted by the form
    if request.method == 'POST':
        token = request.POST.get('stripeToken')

        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            charge = stripe.Charge.create(
                amount=stripe_amount, # amount in cents, again
                currency="cad",
                card=token,
                description="payinguser@example.com"
            )

            send_confirmation(game_connector_id)

            return HttpResponseRedirect(reverse('payment success', args=(quest_type_id, short_name, competition_id, slug)))
        except stripe.CardError, e:
          # The card has been declined
          pass


    args = {}
    args['publishable'] = STRIPE_PUBLIC_KEY
    args['has_paid'] = game_connector.has_paid
    args['amount'] = amount
    return render_to_response('payment/payments.html', args, context_instance=RequestContext(request)) 

def request_quest_payment(request, quest_type_id, short_name, competition_id, slug):
    competition = get_object_or_404(Competition, pk=competition_id)
    game_connector_id = request.session['game_connector_id']
    game_connector = GameInstance.objects.get(pk=game_connector_id)
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    args = {}
    args['competition'] = competition
    args['publishable'] = STRIPE_PUBLIC_KEY
    args['quest_types'] = quest_types
    args.update(csrf(request))
    request.session['game_id'] = team.gameinstance.id
    return render_to_response('payment/payments.html', args, context_instance=RequestContext(request)) 

# Create your views here.

def payment_accepted(request, quest_type_id, short_name, competition_id, slug):
    args ={}
    return render_to_response('payment/thank_you.html', args, context_instance=RequestContext(request)) 
