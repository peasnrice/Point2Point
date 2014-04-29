from django.conf.urls import patterns, url
from sites import views

urlpatterns = patterns('',
    url(r'^$', views.homepage, name='homepage'),
    url(r'^$about/', views.about, name='about'),
)