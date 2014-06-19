from django.conf.urls import patterns, url
from userprofile import views

urlpatterns = patterns('',
    url(r'^$', views.user_profile, name='userprofile'),
    url(r'^getpin/', views.get_pin, name='get pin'),
    url(r'^verifypin/', views.verify_pin, name='verify pin'),
    url(r'^ajax/', views.ajax, name='ajax'),
    url(r'^ajax_send_pin/', views.ajax_send_pin, name='ajax send pin'),
)