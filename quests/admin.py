from django.contrib import admin
from quests.models import Competition, GameInstance, Team, Player, QuestionsSolutionPair, Solution, GameStage, QuestType

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

class GameStageInline(admin.TabularInline):
    model = GameStage
    extra = 3

class GameInstanceAdmin(admin.ModelAdmin):
    inlines = [TeamInline, GameStageInline]

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
admin.site.register(GameStage)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player)
admin.site.register(QuestionsSolutionPair, QuestionsSolutionPairAdmin)
admin.site.register(Solution)
admin.site.register(QuestType)