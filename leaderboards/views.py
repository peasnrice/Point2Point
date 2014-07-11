from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from quests.models import Competition, GameInstance, GameStage, QuestType
from time import strftime
import datetime, timedelta
from django.utils.timezone import utc

class LeaderboardGameData:
    def __init__(self, competition_number_, position_, name_, time_bp_, time_ap_, 
                 average_time_, penalties_):
        self.competition = competition_number_
        self.position = str(position_)
        self.name = name_
        self.time_bp = time_bp_
        self.time_ap = time_ap_
        self.average_time = average_time_ 
        self.penalties = penalties_


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    d["hours"] = "%02d" % (d["hours"],)
    d["minutes"] = "%02d" % (d["minutes"],)
    d["seconds"] = "%02d" % (d["seconds"],)    
    return fmt.format(**d)

# Returns Home Page from url /
def leaderboards(request):
    competition_list = []
    ended_game_list = []
    ongoing_game_list = []
    dnf_game_list = []
    competitions_list = Competition.objects.all().order_by("name")
    number_of_competitions = len(competition_list)
    competition_number = 0
    number_of_teams_to_show = 5
    for competition in competitions_list:
        team_number = 0
        position = 0
        competition_list.append(competition)
        
        game_instances = GameInstance.objects.filter(competition=competition.id).order_by("total_time")
        ended_games = game_instances.filter(ended=True).filter(dnf=False)
        ongoing_games = game_instances.filter(ended=False)
        dnf_games = game_instances.filter(dnf=True)
        
        for ended_game in ended_games:
            if team_number >= number_of_teams_to_show:
                break
            position += 1
            team_name = ended_game.getTeamName()
            time_bp = strfdelta(ended_game.game_time, "{hours}:{minutes}:{seconds}")
            time_ap = strfdelta(ended_game.total_time, "{hours}:{minutes}:{seconds}")
            average_time = strfdelta(ended_game.average_time, "{hours}:{minutes}:{seconds}")
            penalties = ended_game.incorrect_answers + ended_game.location_hints_used + ended_game.clue_hints_used
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time, penalties)
            ended_game_list.append(l)
            team_number += 1

        for ongoing_game in ongoing_games:
            if team_number >= number_of_teams_to_show:
                break
            position = "in progress"
            team_name = ongoing_game.getTeamName()

            time_delta = datetime.timedelta(0)
            if ongoing_game.started == True and ongoing_game.ended == False and ongoing_game.paused == False:
                gs = GameStage.objects.filter(gameinstance=ongoing_game.id).latest('time_stamp')
                time_delta = (datetime.datetime.utcnow().replace(tzinfo=utc) - gs.time_stamp) + ongoing_game.game_time
            else:
                time_delta = ongoing_game.game_time

            time_bp = strfdelta(time_delta, "{hours}:{minutes}:{seconds}")
            time_ap = strfdelta(ongoing_game.total_time, "{hours}:{minutes}:{seconds}")
            average_time = strfdelta(ongoing_game.average_time, "{hours}:{minutes}:{seconds}")
            penalties = ongoing_game.incorrect_answers + ongoing_game.location_hints_used + ongoing_game.clue_hints_used
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time, penalties)
            ongoing_game_list.append(l)
            team_number += 1

        for dnf_game in dnf_games:
            if team_number >= number_of_teams_to_show:
                break
            position = "dnf"
            team_name = dnf_game.getTeamName()
            time_bp = strfdelta(dnf_game.game_time, "{hours}:{minutes}:{seconds}")
            time_ap = strfdelta(dnf_game.total_time, "{hours}:{minutes}:{seconds}")
            average_time = strfdelta(dnf_game.average_time, "{hours}:{minutes}:{seconds}")
            penalties = dnf_game.incorrect_answers + dnf_game.location_hints_used + dnf_game.clue_hints_used
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time, penalties)
            dnf_game_list.append(l)    
            team_number += 1 
            
        competition_number += 1
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    args = {}
    args['competition_list'] = competition_list
    args['ended_game_list'] = ended_game_list
    args['ongoing_game_list'] = ongoing_game_list
    args['dnf_game_list'] = dnf_game_list
    args['quest_types'] = quest_types
    return render_to_response('leaderboards/leaderboards.html', args, context_instance=RequestContext(request)) 

def leaderboard_detail(request, competition_id, slug):
    competition = get_object_or_404(Competition, pk=competition_id)
    ended_game_list = []
    ongoing_game_list = []
    dnf_game_list = []
    competition_number = 0
    position = 0
    
    game_instances = GameInstance.objects.filter(competition=competition.id).order_by("total_time")
    ended_games = game_instances.filter(ended=True).filter(dnf=False)
    ongoing_games = game_instances.filter(ended=False)
    dnf_games = game_instances.filter(dnf=True)
    
    for ended_game in ended_games:
        position += 1
        team_name = ended_game.getTeamName()
        time_bp = strfdelta(ended_game.game_time, "{hours}:{minutes}:{seconds}")
        time_ap = strfdelta(ended_game.total_time, "{hours}:{minutes}:{seconds}")
        average_time = strfdelta(ended_game.average_time, "{hours}:{minutes}:{seconds}")
        penalties = ended_game.incorrect_answers + ended_game.location_hints_used + ended_game.clue_hints_used
        l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time, penalties)
        ended_game_list.append(l)

    for ongoing_game in ongoing_games:
        position = "in progress"
        team_name = ongoing_game.getTeamName()

        time_delta = datetime.timedelta(0)
        if ongoing_game.started == True and ongoing_game.ended == False and ongoing_game.paused == False:
            gs = GameStage.objects.filter(gameinstance=ongoing_game.id).latest('time_stamp')
            time_delta = (datetime.datetime.utcnow().replace(tzinfo=utc) - gs.time_stamp) + ongoing_game.game_time
        else:
            time_delta = ongoing_game.game_time

        time_bp = strfdelta(time_delta, "{hours}:{minutes}:{seconds}")
        time_ap = strfdelta(ongoing_game.total_time, "{hours}:{minutes}:{seconds}")
        average_time = strfdelta(ongoing_game.average_time, "{hours}:{minutes}:{seconds}")
        penalties = ongoing_game.incorrect_answers + ongoing_game.location_hints_used + ongoing_game.clue_hints_used
        l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time, penalties)
        ongoing_game_list.append(l)

    for dnf_game in dnf_games:
        position = "dnf"
        team_name = dnf_game.getTeamName()
        time_bp = strfdelta(dnf_game.game_time, "{hours}:{minutes}:{seconds}")
        time_ap = strfdelta(dnf_game.total_time, "{hours}:{minutes}:{seconds}")
        average_time = strfdelta(dnf_game.average_time, "{hours}:{minutes}:{seconds}")
        penalties = dnf_game.incorrect_answers + dnf_game.location_hints_used + dnf_game.clue_hints_used
        l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time, penalties)
        dnf_game_list.append(l)  
    quest_types = QuestType.objects.filter(front_page=True).order_by('priority')
    args = {}
    args['competition'] = competition
    args['ended_game_list'] = ended_game_list
    args['ongoing_game_list'] = ongoing_game_list
    args['dnf_game_list'] = dnf_game_list
    args['quest_types'] = quest_types
    return render_to_response('leaderboards/leaderboarddetail.html', locals(), context_instance=RequestContext(request)) 