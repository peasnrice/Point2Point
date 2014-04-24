from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^twilio_test/', include('twilio_test.urls')),
    url(r'^quests/'), include('quests.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
