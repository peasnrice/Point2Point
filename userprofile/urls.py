from django.conf.urls import patterns, url, include
from userprofile import views
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.user_profile, name='userprofile'),
    url(r'^getpin/', views.get_pin, name='get pin'),
    url(r'^verifypin/', views.verify_pin, name='verify pin'),
    url(r'^ajax/', views.ajax, name='ajax'),
    url(r'^ajax_send_pin/', views.ajax_send_pin, name='ajax send pin'),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)