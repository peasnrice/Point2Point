from django.shortcuts import render

def request_adventure_payment(request, competition_id, slug):
	competition = get_object_or_404(Competition, pk=competition_id)
    args['competition'] = competition
    args['publishable'] = STRIPE_PUBLIC_KEY
	return render_to_response('/detail.html', args, context_instance=RequestContext(request)) 

# Create your views here.

def payment_accepted(request):
    game = team.gameinstance
    question = game.current_question
    sms_text = competition.getQSPairTextByQNum(question)
    game.createGameStage()    
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
    message = client.messages.create(body=sms_text,
        to=save_team.phone_number,
        from_=TWILIO_NUMBER)

    known_user_numbers = ProfilePhoneNumber.objects.filter(phone_number=save_team.phone_number)
    for known_user in known_user_numbers:
        known_user.user_profile.game_instances.add(game)
        known_user.user_profile.save()

    subject = competition.name
    from_email = 'PointToPoint@pointtopoint.webfactional.com'
    body = "Congratulations team "
    body += team.name
    body += " on signing up for the "
    body += competition.name 
    body += " Point To Point quest!\n\n"
    body += "You should have received a confirmation message on your captains phone number or if not it should arrive shortly!\n"
    body += "You can start the quest whenever you like, just make sure you start it within the allowed time boundries of the quest. "
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
    body += "If you have any question along your way please contact support at andy@pointtopoint.webfactional.com "
    body += "and we will get back to you as quickly as possible\n\n"
    body += "\n\nHappy questing team "
    body += team.name
    body += "!"
    to_email = team.email
    send_mail(subject, body, from_email,[to_email], fail_silently=False)
    
    return HttpResponseRedirect('/')
