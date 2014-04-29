from django.conf.urls import patterns, include, url
from about import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.about, name='about'),
)
