from django.conf.urls import url, include

from . import views

app_name = 'twitterscheduler'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tweet/create/$', views.create_scheduled_tweet, name='create-scheduled-tweet'),
]
