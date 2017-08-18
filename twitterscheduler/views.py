from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from allauth.socialaccount.models import SocialToken, SocialApp

from .models import Tweet

import tweepy
import time


@login_required
def index(request):
    access_token = get_object_or_404(SocialToken, account__user=request.user, app__provider='twitter')
    # token, token_secret = access_token.token, access_token.token_secret
    print(f'user: {request.user}')
    print(f'access_token: {access_token.token}')

    # sync_tweets_from_twitter(request.user, access_token.token, access_token.token_secret)

    # if user_tweets:
    #     return JsonResponse({'tweet': user_tweets[0]._json})

    user_tweets = Tweet.objects.filter(user=request.user)

    context = {
        'access_token': access_token,
        'user_tweets': user_tweets,
    }

    return render(request, 'twitterscheduler/index.html', context=context)


def sync_tweets_from_twitter(user, access_token, token_secret):
    """
    Gets the users tweets from twitter and saves them to db.
    Does the syncing in background.
    Will only save tweets 10 minutes or older to prevent race conditions with the tweet scheduler.
    """
    twitter_api = get_authed_tweepy(access_token, token_secret)

    tweets_twitter = twitter_api.user_timeline()
    tweets_db = Tweet.objects.filter(user=user)

    for tweet_twitter in tweets_twitter:
        tweet_in_db = False
        for tweet_db in tweets_db:
            if tweet_db.tweet_id == tweet_twitter.id_str:
                tweet_in_db = True
                break

        if not tweet_in_db:
            new_tweet = Tweet(tweet_id=tweet_twitter.id_str, user=user, text=tweet_twitter.text,
                              time_posted_at=tweet_twitter.created_at, is_posted=True)
            new_tweet.save()

    return tweets_twitter
    # return JsonResponse({'tweet': user_tweets[0]._json})


def get_authed_tweepy(access_token, token_secret):
    """Returns an authed instance of the twitter api wrapper tweepy for a given user."""
    social_app_twitter = get_object_or_404(SocialApp, provider='twitter')

    auth = tweepy.OAuthHandler(social_app_twitter.client_id, social_app_twitter.secret)
    auth.set_access_token(access_token, token_secret)
    return tweepy.API(auth)

