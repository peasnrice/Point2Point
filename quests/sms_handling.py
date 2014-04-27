from quests.models import Competition, Team, GameInstance, GameStage

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
                    elif game.current_question < game.competition.getQuestLength():
                        game.current_question += 1
                        game.save()
                    else:
                        game.ended = True
                        game.current_question += 1
                        game.save()
                    game.createGameStage()
                    if game.ended == True:
                        game.total_time = game.getTotalTime()
                        game.game_time = game.getGameTime()
                        game.penalty_time = game.getPenaltyTime()
                        game.save()

                        s = game.total_time.seconds
                        hours, remainder = divmod(s, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        total_time = '%s:%s:%s' % (hours, minutes, seconds)

                        s = game.total_time.seconds
                        hours, remainder = divmod(s, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        game_time = '%s:%s:%s' % (hours, minutes, seconds)

                        s = game.penalty_time.seconds
                        hours, remainder = divmod(s, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        penalty_time = '%s:%s:%s' % (hours, minutes, seconds)

                        s = game.total_time.seconds + game.penalty_time.seconds
                        hours, remainder = divmod(s, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        overall_time = '%s:%s:%s' % (hours, minutes, seconds)

                        return_message = "Congratulations! Your total time (including breaks) was " + total_time + "."
                        if game.penalty_time.seconds == 0:
                            return_message += ". Your overall time, with no penalties, was " + overall_time + "."
                        else:
                            return_message += ". Your game time could have been " + game_time
                            return_message += " but sadly you picked up " + penalty_time + " in penalties"
                            return_message += " bringing your overall time to " + overall_time +"."
                        return_message += " Thank you for playing! Please give use feedback, good or bad, at feedback@Point2Point.com!"
                        return_message += " We hope to see you again soon, happy questing!"
                    else:
                        return_message = game.competition.getQuestion(game.current_question)
                    sln_found = True
                    break
            if sln_found == False:
                game_stage = GameStage.objects.filter(gameinstance=game.id).get(stage=game.current_question)
                if game_stage.is_pause == False:
                    game.addPenalty(5)
                    return_message = "try again, a penalty of 5 minutes has been added!"
                else:
                    return_message = "Sorry we didn't understand"
        # they exist but uhoh they don't have a game. let them know
        else:
            return_message = "Sorry, you don't appear to be participating in an active game"
    return return_message