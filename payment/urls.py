from django.conf.urls import patterns, url
from quests import web_views

urlpatterns = patterns('',
    url(r'^(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/payments$', views.request_adventure_payment, name='adventure payment'),
    #url(r'^leaderboards/$', web_views.leaderboards, name='leaderboards'),
)