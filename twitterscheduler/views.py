from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Tweet, ScheduledTweet, Profile
from .forms import CreateScheduleTweetForm
from .tasks import tweet_task, sync_tweets_task

import datetime


@login_required
def index(request):
    profile = Profile.objects.get(user=request.user)

    if not profile.synced_tweets_recently():
        sync_tweets_task.delay(request.user.username)

    user_tweets = Tweet.objects.filter(user=request.user, is_posted=True)
    scheduled_tweets = ScheduledTweet.objects.filter(tweet__user=request.user)


    context = {
        'user_tweets': user_tweets,
        'scheduled_tweets': scheduled_tweets,
    }
    return render(request, 'twitterscheduler/index.html', context=context)


@login_required
def create_scheduled_tweet(request):
    if request.method == 'POST':
        tweet_form = CreateScheduleTweetForm(request.POST)
        if tweet_form.is_valid():
            new_tweet = Tweet.objects.create(user=request.user, text=tweet_form.cleaned_data['text'])
            new_scheduled_tweet = ScheduledTweet.objects.create(tweet=new_tweet,
                                                                time_to_tweet=tweet_form.cleaned_data['time_to_tweet'])
            tweet_task.apply_async(
                (request.user.username, new_scheduled_tweet.id),
                eta=tweet_form.cleaned_data['time_to_tweet']
            )
            return HttpResponseRedirect(reverse('twitterscheduler:index'))
    else:
        tweet_form = CreateScheduleTweetForm(initial={'time_to_tweet': timezone.now()+datetime.timedelta(minutes=5)})
    return render(request, 'twitterscheduler/create_scheduled_tweet.html', context={'tweet_form': tweet_form})
