from django.conf.urls import patterns, url
from quests import web_views

urlpatterns = patterns('',
    url(r'^$', web_views.index, name='index'),
    url(r'^(?P<competition_id>\d+)/$', web_views.detail, name='detail'),
    url(r'^verify_sms/$', web_views.verify_sms, name='verify_sms'),
    url(r'^leaderboards/$', web_views.leaderboards, name='leaderboards'),
    #url(r'^leaderboards/(?P<competition_id>\d+)/$', web_views.leaderboard_detail, name='leaderboard_detail'),
    url(r'^goodbye/$', 'django_twilio.views.say', {
        'text': 'Adios Bandito!',
        'voice': 'woman',
        'language': 'es',
        'loop': 0,
    }),
)