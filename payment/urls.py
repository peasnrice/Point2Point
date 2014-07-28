from django.conf.urls import patterns, url
from payment import views

urlpatterns = patterns('',
    url(r'^$', views.payment , name='payment'),
)