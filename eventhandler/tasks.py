from Point2Point.settings import *
from quests.models import GameInstance, Team, QuestionsSolutionPair
from celery.decorators import task
from twilio.rest import TwilioRestClient

@task()
def add_to_count():
    try:
        sc = SampleCount.objects.get(pk=1)
    except:
        sc = SampleCount()
    sc.num = sc.num + 1
    sc.save()

def send_msg(to_number, text):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
 
    message = client.messages.create(to=to_number, from_="+14385001559",
                                     body=text)

@task()
def resumeGame(game_pk, team_pk, question_when_called):
    game = GameInstance.objects.get(pk=game_pk)
    if question_when_called == game.current_question:
        team = Team.objects.get(pk=team_pk)
        game.current_question += 1
        game.createGameStage()
        game.updateGameTime()
        game.answered_incorrectly = False
        game.clue_hint_used = False
        game.location_hint_used = False
        game.save()

        question_text = QuestionsSolutionPair.objects.filter(competition=game.competition).get(question_number=game.current_question).question_text
        send_text = "Your break is over! " + question_text
        send_msg(team.phone_number, send_text)



