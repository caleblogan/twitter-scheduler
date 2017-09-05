from django.conf.urls import url, include

from . import views

app_name = 'twitterscheduler'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tweet/create/$', views.create_scheduled_tweet, name='create-scheduled-tweet'),
    url(r'^scheduled-tweet/(?P<pk>\d+)/edit/$', views.update_scheduled_tweet, name='edit-scheduled-tweet'),
]
