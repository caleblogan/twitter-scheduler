from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from allauth.socialaccount.models import SocialToken, SocialApp

from .models import Tweet

import tweepy
import datetime


@login_required
def index(request):
    # access_token = get_object_or_404(SocialToken, account__user=request.user, app__provider='twitter')
    # token, token_secret = access_token.token, access_token.token_secret
    # print(f'user: {request.user}')
    # print(f'access_token: {access_token.token}')

    user_tweets = Tweet.objects.filter(user=request.user)

    context = {
        'user_tweets': user_tweets,
    }
    return render(request, 'twitterscheduler/index.html', context=context)


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

