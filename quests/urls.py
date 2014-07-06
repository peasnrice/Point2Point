from django.conf.urls import patterns, url
from quests import web_views

urlpatterns = patterns('',
    url(r'^$', web_views.quests, name='quests'),
    url(r'^casual/$', web_views.casual_quests, name='casual quests'),
    url(r'^adventure/$', web_views.adventure_quests, name='casual quests'),
    url(r'^evening/$', web_views.evening_quests, name='evening quests'),
    url(r'^casual/(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/$', web_views.casual_quest_detail, name='casual_detail'),
    url(r'^evening/(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/$', web_views.evening_quest_detail, name='evening_detail'),
    url(r'^adventure/(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/$', web_views.adventure_quest_detail, name='adventure_detail'),
    url(r'^verify_sms/$', web_views.verify_sms, name='verify_sms'),
    #url(r'^leaderboards/$', web_views.leaderboards, name='leaderboards'),
)