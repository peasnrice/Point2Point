from django.views.generic import RedirectView
from django.conf.urls import patterns, url
from users import views
from userprofile import views as profile_views

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='profile/')),
    url(r'^profile/$', profile_views.user_profile, name='userprofile'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
)