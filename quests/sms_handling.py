from quests.models import Competition, Team, GameInstance

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
            solutions = game.competition.getSolutions(game.current_question)
            sln_found = False
            for solution in solutions:
                if from_text == solution.solution_text.lower():
                    if game.current_question == 0:
                        game.started = True
                        game.current_question += 1
                        game.save()
                        #Time Stamp
                    elif game.current_question < game.competition.getQuestLength():
                        game.current_question += 1
                        game.save()
                        #check if pause is needed
                    else:
                        game.ended = True
                        game.current_question += 1
                        game.save()
                        #stop timer
                    
                    game.createGameStage()                    
                    
                    if game.ended == True:
                        return_message = game.competition.congratulation
                        game.total_time = game.getTotalTime()
                        game.save()
                    else:
                        return_message = game.competition.getQuestion(game.current_question)
                    sln_found = True
                    break
            if sln_found == False:
                return_message = "try again"
        # they exist but uhoh they don't have a game. let them know
        else:
            return_message = "Sorry, you don't appear to be participating in an active game"
    return return_message