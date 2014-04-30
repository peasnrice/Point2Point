from django.shortcuts import render, get_object_or_404, render_to_response, render, RequestContext
from quests.models import Competition, GameInstance
from time import strftime

class LeaderboardGameData:
    def __init__(self, competition_number_, position_, name_, time_bp_, time_ap_, average_time_):
        self.competition = competition_number_
        self.position = str(position_)
        self.name = name_
        self.time_bp = time_bp_
        self.time_ap = time_ap_
        self.average_time = average_time_  

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

# Returns Home Page from url /
def leaderboards(request):
    competition_list = []
    ended_game_list = []
    ongoing_game_list = []
    dnf_game_list = []
    competitions_list = Competition.objects.all()
    number_of_competitions = len(competition_list)
    competition_number = 0
    for competition in competitions_list:
        position = 0
        competition_list.append(competition.name)
        
        game_instances = GameInstance.objects.filter(competition=competition.id).order_by("game_time")
        ended_games = game_instances.filter(ended=True).filter(dnf=False)
        ongoing_games = game_instances.filter(ended=False)
        dnf_games = game_instances.filter(dnf=True)
        
        for ended_game in ended_games:
            position += 1
            team_name = ended_game.getTeamName()
            time_bp = strfdelta(ended_game.game_time, "{hours}h {minutes}m {seconds}s")
            time_ap = strfdelta(ended_game.total_time, "{hours}h {minutes}m {seconds}s")
            average_time = strfdelta(ended_game.average_time, "{hours}h {minutes}m {seconds}s")
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time)
            ended_game_list.append(l)

        for ongoing_game in ongoing_games:
            position = "in progress"
            team_name = ongoing_game.getTeamName()
            time_bp = strfdelta(ongoing_game.game_time, "{hours}h {minutes}m {seconds}s")
            time_ap = strfdelta(ongoing_game.total_time, "{hours}h {minutes}m {seconds}s")
            average_time = strfdelta(ongoing_game.average_time, "{hours}h {minutes}m {seconds}s")
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time)
            ongoing_game_list.append(l)  

        for dnf_game in dnf_games:
            position = "dnf"
            team_name = dnf_game.getTeamName()
            time_bp = strfdelta(dnf_game.game_time, "{hours}h {minutes}m {seconds}s")
            time_ap = strfdelta(dnf_game.total_time, "{hours}h {minutes}m {seconds}s")
            average_time = strfdelta(dnf_game.average_time, "{hours}h {minutes}m {seconds}s")
            l = LeaderboardGameData(competition_number, position, team_name, time_bp, time_ap, average_time)
            dnf_game_list.append(l)     
            
        competition_number += 1
    context = {'competition_list': competition_list}
    return render_to_response('leaderboards/leaderboards.html', locals(), context_instance=RequestContext(request)) 
