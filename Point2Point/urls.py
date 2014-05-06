from django.conf.urls import patterns, include, url
from django.contrib import admin
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
)
