from django.conf.urls import patterns, url
from eventhandler import views

urlpatterns = patterns('',
    url(r'^$', views.test_async, name='test_async'),
)