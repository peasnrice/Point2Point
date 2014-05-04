from quests.models import Competition, Team, GameInstance, GameStage, QuestionsSolutionPair, Solution
from datetime import datetime, time, timedelta

def correctAnswer(game):
    if game.current_question == 0:
        game.started = True
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

    if game.ended == True:
        total_time = strfdelta(game.total_time, "{hours}h {minutes}m {seconds}s")
        game_time = strfdelta(game.game_time, "{hours}h {minutes}m {seconds}s")
        penalty_time = strfdelta(game.penalty_time, "{hours}h {minutes}m {seconds}s")
        average_time = strfdelta(game.average_time, "{hours}h {minutes}m {seconds}s")

        return_message = "Congratulations!"
        if game.penalty_time.seconds == 0:
            return_message += " Your overall time, with no penalties, was " + total_time + "."
        else:
            return_message += " Your game time could have been " + game_time
            return_message += " but sadly you picked up " + penalty_time + " in penalties"
            return_message += " bringing your overall time to " + total_time +".\n"
        return_message += "Thank you for playing! Please give use feedback, good or bad, at feedback@Point2Point.com!\n"
        return_message += "We hope to see you again soon, happy questing!"
    else:
        return_message = game.competition.getQuestion(game.current_question)
    return return_message

def incorrectAnswer(game):
    response_text = ""
    current_question = QuestionsSolutionPair.objects.filter(competition=game.competition).get(question_number=game.current_question)
    solution = Solution.objects.filter(questions_solution_pair=current_question)
    if current_question.is_pause:
        if solution:
            return "%s \'%s\' %s" %("Sorry we didn't catch that, reply with", solution[0].solution_text, "to continue")
        else:
            return "%s %s" %("Sorry we didn't catch that, please reply with 'repeat' to repeat instructions")
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
    current_question = QuestionsSolutionPair.objects.filter(competition=game.competition).get(question_number=game.current_question)
    skip_text = ""
    if current_question.is_pause == True:
        skip_text = "Sorry, you can't skip a break like this, please reply with 'repeat' to see what word to use D= ???"
    elif game.current_question < game.competition.getQuestLength():
        game.current_question += 1
        game.penalty_time += timedelta(minutes=30)
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
    skip_text = "%s.\n\n%s" %("You skipped the question but at a price of 30 minutes.", current_question.question_text)
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
    return fmt.format(**d)

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