from django.conf.urls import patterns, url
from users import views

urlpatterns = patterns('',
    url(r'^$', views.users, name='users'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
)