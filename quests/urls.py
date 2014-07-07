from django.conf.urls import patterns, url
from quests import web_views
from payment import views as payment_views

urlpatterns = patterns('',
    url(r'^$', web_views.quests, name='quests'),
    url(r'^(?P<quest_type_id>\d+)/(?P<short_name>[-\w\d]+)/$', web_views.quest_list_type, name='quest_type'),
    url(r'^(?P<quest_type_id>\d+)/(?P<short_name>[-\w\d]+)/(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/register/$', web_views.quest_register_team, name='quest_register_team'),
    url(r'^(?P<quest_type_id>\d+)/(?P<short_name>[-\w\d]+)/(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/payment/$', payment_views.request_quest_payment, name='quest payment'),
    url(r'^(?P<quest_type_id>\d+)/(?P<short_name>[-\w\d]+)/(?P<competition_id>\d+)/(?P<slug>[-\w\d]+)/success/$', payment_views.payment_accepted, name='payment success'),
    url(r'^verify_sms/$', web_views.verify_sms, name='verify_sms'),
    #url(r'^leaderboards/$', web_views.leaderboards, name='leaderboards'),
)