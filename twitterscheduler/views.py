from django.shortcuts import render, get_object_or_404, reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone

from allauth.socialaccount.models import SocialToken, SocialApp

from .models import Tweet, ScheduledTweet
from .forms import CreateScheduleTweetForm
from .tasks import add_task, tweet_task

import tweepy
import datetime


@login_required
def index(request):
    # access_token = get_object_or_404(SocialToken, account__user=request.user, app__provider='twitter')
    # token, token_secret = access_token.token, access_token.token_secret

    user_tweets = Tweet.objects.filter(user=request.user)

    context = {
        'user_tweets': user_tweets,
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
            # print(f'user: {request.user.username}  sch_tweet: {new_scheduled_tweet.id}')
            tweet_task.apply_async(
                (request.user.username, new_scheduled_tweet.id),
                eta=tweet_form.cleaned_data['time_to_tweet']
            )
            return HttpResponseRedirect(reverse('twitterscheduler:index'))
    else:
        tweet_form = CreateScheduleTweetForm(initial={'time_to_tweet': timezone.now()+datetime.timedelta(minutes=5)})
    return render(request, 'twitterscheduler/create_scheduled_tweet.html', context={'tweet_form': tweet_form})


def sync_tweets_from_twitter(user, access_token, token_secret):
    """
    Gets the users tweets from twitter and saves them to db.
    Does the syncing in background.
    Will only save tweets 5 minutes or older to prevent race conditions with the tweet scheduler.
    """
    twitter_api = get_authed_tweepy(access_token, token_secret)

    tweets_twitter = twitter_api.user_timeline()
    tweets_db_map = {twt.tweet_id:twt for twt in Tweet.objects.filter(user=user)}

    for tweet_twit in tweets_twitter:
        if tweet_twit.id_str not in tweets_db_map:
            if timezone.now() - tweet_twit.created_at >= datetime.timedelta(minutes=5):
                new_tweet = Tweet(tweet_id=tweet_twit.id_str, user=user, text=tweet_twit.text,
                                  time_posted_at=tweet_twit.created_at, is_posted=True)
                new_tweet.save()


def get_authed_tweepy(access_token, token_secret):
    """Returns an authed instance of the twitter api wrapper tweepy for a given user."""
    social_app_twitter = get_object_or_404(SocialApp, provider='twitter')

    auth = tweepy.OAuthHandler(social_app_twitter.client_id, social_app_twitter.secret)
    auth.set_access_token(access_token, token_secret)
    return tweepy.API(auth)

