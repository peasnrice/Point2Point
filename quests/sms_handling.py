from Point2Point.settings import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_NUMBER
from quests.models import Competition, Team, GameInstance, GameStage, QuestionsSolutionPair, Solution
from eventhandler.tasks import resumeGame
from twilio.rest import TwilioRestClient
from datetime import timedelta
import datetime
from django.utils.timezone import utc
from eventhandler.tasks import add_to_count, send_msg, resumeGame

def send_msg(to_number, text):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID,
                              TWILIO_AUTH_TOKEN)
 
    message = client.messages.create(to=to_number, from_=TWILIO_NUMBER,
                                     body=text)

def game_logic(from_number, from_text):
    teams = Team.objects.filter(phone_number=from_number)

    return_message = ""
    if not teams:
        return_message = "Sorry, you aren't registered in an active Quest, register at www.Point2Point.com"
    # otherwise let's see if they are already playing
    else:
        has_active_game = False
        active_team = Team()
        for team in teams:
            if team.gameinstance.ended == False:
                has_active_game = True
                active_team = team
                break
        # active game detected! start verifying the message
        if has_active_game == True:
            game = active_team.gameinstance
            from_text = from_text.lower()
            
            if from_text == "game help":
                return_message = help(game)

            elif from_text =="repeat":
                return_message = repeat(game)
            
            elif from_text == "game info":
                return_message = gameInfo(game)
            
            elif from_text == "game quit":
                return_message = quit(game)

            elif from_text == "clue hint":
                return_message = clueHint(game)
            
            elif from_text == "location hint":
                return_message = locationHint(game)

            elif from_text == "skip":
                return_message = skip(game)

            else:
                solutions = game.competition.getSolutions(game.current_question)
                sln_found = False
                for solution in solutions:
                    if from_text == solution.solution_text.lower():
                        return_message = correctAnswer(game)
                        sln_found = True
                        break
                if sln_found == False:
                    return_message = incorrectAnswer(game)
        # they exist but uhoh they don't have a game. let them know
        else:
            return_message = "Sorry, you don't appear to be participating in an active game"
    return return_message

#if a correct answer is found we check to see if the user has finished
def correctAnswer(game):
    if game.current_question == 0:
        check_time_message = checkTime(game)
        if check_time_message:
            return check_time_message
        else:
            game.started = True
            game.date_started = datetime.datetime.utcnow().replace(tzinfo=utc)
            game.current_question += 1
            game.save()
    elif game.current_question < game.competition.getQuestLength():
        game.current_question += 1
        game.save()
    else:
        game.ended = True
        game.current_question += 1
        game.save()
    game.createGameStage()
    game.updateGameTime()
    game.answered_incorrectly = False
    game.clue_hint_used = False
    game.location_hint_used = False
    game.save()

    qs = QuestionsSolutionPair.objects.filter(competition=game.competition)
    q = qs.filter(question_number=game.current_question)

    if game.ended == True:
        total_time = strfdelta(game.total_time, "{hours}:{minutes}:{seconds}")
        game_time = strfdelta(game.game_time, "{hours}:{minutes}:{seconds}")
        penalty_time = strfdelta(game.penalty_time, "{minutes}")
        average_time = strfdelta(game.average_time, "{hours}:{minutes}:{seconds}")

        return_message = "Congratulations!"
        if game.penalty_time.seconds == 0:
            return_message += " Your overall time, with no penalties, was " + total_time + "."
        else:
            return_message += " Your game time could have been " + game_time
            return_message += " but sadly you picked up " + penalty_time + " in penalties"
            return_message += " bringing your overall time to " + total_time +".\n"
        return_message += "Thank you for playing! Please give use feedback, good or bad, at feedback@Point2Point.com!\n"
        return_message += "We hope to see you again soon, happy questing!"
    elif game.current_question != 0:
        if q:
            if q[0].is_pause == True:
                game.paused = True
                game.save()
                team = Team.objects.get(gameinstance=game)
                resumeGame.apply_async([game.pk,team.pk,game.current_question],countdown=q[0].pause_duration.seconds)
                return "Correct! Take a %s break! %s" %(strfdelta(q[0].pause_duration,"{minutes} minute"), game.competition.getQuestion(game.current_question))
            else:
                game.paused = False
                game.save()                
                return game.competition.getQuestion(game.current_question) 
        else:
            return game.competition.getQuestion(game.current_question) 
    else:
        return game.competition.getQuestion(game.current_question) 
    return return_message

def incorrectAnswer(game):
    response_text = ""
    current_question = QuestionsSolutionPair.objects.filter(competition=game.competition).get(question_number=game.current_question)
    solution = Solution.objects.filter(questions_solution_pair=current_question)
    if current_question.is_pause:
        if solution:
            return "%s \'%s\' %s" %("Sorry we didn't catch that, reply with", solution[0].solution_text, "to continue")
        else:
            return "%s" %("Sorry we didn't catch that, please reply with 'repeat' to repeat instructions")
    else:          
        if game.answered_incorrectly:
            game.penalty_time += timedelta(minutes=10)
            game.save()
            return "Sorry, that answer was not correct.\nBe careful, that's a 10 minute penalty. You can reply with \'skip\' to advance but you will take on a 30 minute penalty!"
        elif current_question.is_pause == False:
            if game.clue_hints_used > 0:
                response_text = "Sorry, that answer was not correct.\nHere is a clue but you have picked up an additional 10 minutes penalty!"
                game.incorrect_answers += 1
                game.penalty_time += timedelta(minutes=10)
                game.save()
            else:
                response_text = "Sorry, that answer was not correct.\nHere is a clue, any more mistakes will cost you a 10 minute penalty!"
            game.clue_hints_used += 1
            game.clue_hint_used = True
            game.save()
    game.answered_incorrectly = True  
    game.save()
    return "%s %s" %(response_text, current_question.clue_hint_text)

def clueHint(game):
    hint_text = ""
    current_question = QuestionsSolutionPair.objects.filter(competition=game.competition).get(question_number=game.current_question)
    if game.clue_hint_used:
        return current_question.clue_hint_text
    elif current_question.is_pause == False:
        if game.clue_hints_used > 0 :
            hint_text = "You have used another clue hint, an additional 10 minutes has been added to your total time!"
            game.penalty_time += timedelta(minutes=10)
        else:
            hint_text = "You have used your free clue hint, any more will cost you a 10 minute penalty!"
        game.clue_hints_used += 1
        game.clue_hint_used = True
        game.save()
    return "%s %s" %(hint_text, current_question.clue_hint_text)

def locationHint(game):
    hint_text = ""
    current_question = QuestionsSolutionPair.objects.filter(competition=game.competition).get(question_number=game.current_question)
    if game.location_hint_used:
        return current_question.location_hint_text
    elif current_question.is_pause == False:
        if game.location_hints_used > 0 :
            hint_text = "You have used another location hint, an additional 10 minutes has been added to your total time!"
            game.penalty_time += timedelta(minutes=10)
        else:
            hint_text = "You have used your free location hint, any more will cost you a 10 minute penalty!"
        game.location_hints_used += 1
        game.location_hint_used = True
        game.save()
    return "%s %s" %(hint_text, current_question.location_hint_text)

def skip(game):
    q_set = QuestionsSolutionPair.objects.filter(competition=game.competition)
    current_question = q_set.get(question_number=game.current_question)
    skip_text = ""
    if current_question.is_pause == True:
        game.paused = True
        game.save()
        return "%s.\n\n%s" %("Sorry, you can't skip a break like this.", current_question.question_text)
    elif game.current_question < game.competition.getQuestLength():
        game.paused = False
        game.current_question += 1
        game.penalty_time += timedelta(minutes=30)
        game.save()
        current_question = q_set.get(question_number=game.current_question)
        if current_question.is_pause == True:
            game.paused = True
            game.save()
            skip_text = "%s.\n\nTake a %s break! %s" %("You skipped the question but at a price of 30 minutes.", strfdelta(current_question.pause_duration,"{minutes} minute"), current_question.question_text)
        else:
            game.paused = False
            game.save()
            skip_text = "%s.\n\n%s" %("You skipped the question but at a price of 30 minutes.", current_question.question_text)
    else:
        game.ended = True
        game.penalty_time += timedelta(minutes=30)
        game.updateGameTime()
        game.current_question += 1
        game.save()
        total_time = strfdelta(game.total_time, "{hours}:{minutes}:{seconds}")
        game_time = strfdelta(game.game_time, "{hours}:{minutes}:{seconds}")
        penalty_time = strfdelta(game.penalty_time, "{hours}:{minutes}")
        average_time = strfdelta(game.average_time, "{hours}:{minutes}:{seconds}")

        skip_text = "Aww you skipped the final question and picked up a 30 minute penalty =(\n\n"
        if game.penalty_time.seconds == 0:
            skip_text += " Your overall time, with no penalties, was " + total_time + "."
        else:
            skip_text += "Your game time could have been " + game_time
            skip_text += " but sadly you picked up " + penalty_time + " in penalties"
            skip_text += " bringing your overall time to " + total_time +".\n"
        skip_text += "Thank you for playing! Please give use feedback, good or bad, at feedback@Point2Point.com!\n"
        skip_text += "We hope to see you again soon, happy questing!"
    game.createGameStage()
    game.updateGameTime()
    game.answered_incorrectly = False
    game.clue_hint_used = False
    game.location_hint_used = False
    game.save()
    return skip_text

def addNumber(game):
    return 0

def quit(game):
    game.dnf = True
    game.ended = True
    game.save()
    return "you have left the game! =( if this was in error contact support @XXX-XXX-XXXX"

def help(game):
    help_text = "'repeat' - Repeats current question.\n"
    help_text += "'game info' - displays game information.\n"
    help_text += "'game quit' - WARNING! Quits the game, you can't get it back!\n"
    return help_text

def repeat(game):
    return game.competition.getQuestion(game.current_question)

def gameInfo(game):
    gi_text = "Stage no. " + str(game.current_question) + "/" + str(game.competition.getQuestLength()) + "\n"
    
    time = ["0h 0m 0s", "0h 0m 0s", "0h 0m 0s"]

    if game.current_question != 0:
        time = game.getTimeAsText()

    gi_text += "avg solve time: " + time[0] + "\n"
    gi_text += "game time: " + time[1] + "\n"
    gi_text += "penalty time: " + time[2] + "\n"
    return gi_text

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    d["hours"] = "%02d" % (d["hours"],)
    d["minutes"] = "%02d" % (d["minutes"],)
    d["seconds"] = "%02d" % (d["seconds"],)  
    return fmt.format(**d)

def daysToInts(competition):
    days = [0] *7
    if competition.monday == True:
        days[0] = 1
    if competition.tuesday == True:
        days[1] = 1
    if competition.wednesday == True:
        days[2] = 1
    if competition.thursday == True:
        days[3] = 1
    if competition.friday == True:
        days[4] = 1
    if competition.saturday == True:
        days[5] = 1
    if competition.sunday == True:
        days[6] = 1
    return days

def checkTime(game):
    competition = game.competition
    current_date = datetime.datetime.utcnow().replace(tzinfo=utc)

    if current_date < competition.start_date:
        return "Sorry, this quest starts on " + str(competition.start_date) + ", please contact support if there is a problem"   
    if current_date > competition.end_date:
        return "Sorry, this quest ended on " + str(competition.end_date) + ", please contact support if this is a problem"   

    weekday = datetime.datetime.utcnow().replace(tzinfo=utc).weekday()
    days_available = daysToInts(competition)
    if days_available[weekday] != 1:
        return "Sorry, we can't let you start today :(\n\nPlease check online to see when you can participate."

    if current_date.time() > competition.start_time_latest:
        return "Sorry, the latest time you can start this quest is at " + str(competition.start_time_latest) +" as it may ruin your enjoyment. Please come back on another valid day during the valid time period. You may check quest availability on our website"
    if current_date.time() < competition.start_time_earliest:
        return "Sorry, the earliest time you can start this quest is at " + str(competition.start_time_earliest) +" as it may ruin your enjoyment. Please come back at the start time or on another valid day during the valid time period. You may check quest availability on our website"


