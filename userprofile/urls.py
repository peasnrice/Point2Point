from django.conf.urls import patterns, url
from userprofile import views

urlpatterns = patterns('',
    url(r'^$', views.user_profile, name='userprofile'),
    url(r'^getpin/', views.get_pin, name='get pin'),
    url(r'^verifypin/', views.verify_pin, name='verify pin'),
)