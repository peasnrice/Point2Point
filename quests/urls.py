from django.conf.urls import patterns, url
from quests import web_views

urlpatterns = patterns('',
    url(r'^$', web_views.quests, name='quests'),
    url(r'^(?P<competition_id>\d+)/$', web_views.detail, name='detail'),
    url(r'^verify_sms/$', web_views.verify_sms, name='verify_sms'),
    url(r'^leaderboards/$', web_views.leaderboards, name='leaderboards'),
)