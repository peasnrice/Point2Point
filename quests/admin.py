from django.contrib import admin
from quests.models import Competition, GameInstance, Penalty, Team, Player, QuestionsSolutionPair, Solution

class GameSolutionInline(admin.TabularInline):
    model = GameInstance
    extra = 0

class QuestionsSolutionPairInline(admin.TabularInline):
    model = QuestionsSolutionPair
    extra = 3

class CompetitionAdmin(admin.ModelAdmin):
    inlines = [QuestionsSolutionPairInline, GameSolutionInline, ]

class TeamInline(admin.TabularInline):
    model = Team
    extra = 0

class PenaltyInline(admin.TabularInline):
    model = Penalty
    extra = 0

class GameInstanceAdmin(admin.ModelAdmin):
    inlines = [TeamInline, PenaltyInline]

class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 3

class QuestionsSolutionPairAdmin(admin.ModelAdmin):
    inlines = [SolutionInline]

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0

class TeamAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]


admin.site.register(Competition, CompetitionAdmin)
admin.site.register(GameInstance, GameInstanceAdmin)
admin.site.register(Penalty)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player)
admin.site.register(QuestionsSolutionPair, QuestionsSolutionPairAdmin)
admin.site.register(Solution)

