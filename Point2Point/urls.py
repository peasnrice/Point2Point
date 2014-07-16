from django.conf.urls import patterns, include, url
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('home.urls')),
    url(r'^quests/', include('quests.urls')),
    url(r'^leaderboards/', include('leaderboards.urls')),
    url(r'^about/', include('about.urls')),
    url(r'^contact/', include('contact.urls')),
   	url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     {'next_page': '/'}),
   	url(r'^accounts/', include('allauth.urls')),    
    url(r'^profile/', include('userprofile.urls')),
    url(r'^howtoplay/', include('howtoplay.urls')),  
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),  
)
