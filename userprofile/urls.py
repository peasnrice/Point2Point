from django.conf.urls import patterns, url
from userprofile import views

urlpatterns = patterns('',
    url(r'^$', views.user_profile, name='userprofile'),
)