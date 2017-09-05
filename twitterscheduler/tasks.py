import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import ScheduledTweet, Tweet, Profile

import tweepy
from allauth.socialaccount.models import SocialToken, SocialApp
from celery import shared_task


@shared_task
def tweet_task(username, scheduled_tweet_id):
    user = User.objects.get(username=username)
    access_token = SocialToken.objects.get(account__user=user, app__provider='twitter')
    twitter = get_authed_tweepy(access_token.token, access_token.token_secret)
    scheduled_tweet = ScheduledTweet.objects.get(id=scheduled_tweet_id)

    tweet_twitter = twitter.update_status(status=scheduled_tweet.tweet.text)
    tweet_db = Tweet.objects.get(pk=scheduled_tweet.tweet.id)
    tweet_db.tweet_id = tweet_twitter.id_str
    tweet_db.time_posted_at = scheduled_tweet.time_to_tweet
    tweet_db.is_posted = True
    tweet_db.save()
    scheduled_tweet.delete()

    return f'sent tweet for user {user} - {scheduled_tweet.tweet.text}'


@shared_task
def sync_tweets_task(username):
    """
    Gets the users tweets from twitter and saves them to db.
    Does the syncing in background.
    Will only save tweets 5 minutes or older to prevent race conditions with the tweet scheduler.
    """
    user = User.objects.get(username=username)
    access_token = SocialToken.objects.get(account__user=user, app__provider='twitter')
    twitter_api = get_authed_tweepy(access_token.token, access_token.token_secret)

    tweets_twitter = twitter_api.user_timeline()
    tweets_db_map = {twt.tweet_id: twt for twt in Tweet.objects.filter(user=user)}

    for tweet_twit in tweets_twitter:
        tweet_twit.created_at = tweet_twit.created_at.replace(tzinfo=timezone.utc)
        if tweet_twit.id_str not in tweets_db_map:
            if timezone.now() - tweet_twit.created_at >= datetime.timedelta(minutes=5):
                new_tweet = Tweet(tweet_id=tweet_twit.id_str, user=user, text=tweet_twit.text,
                                  time_posted_at=tweet_twit.created_at, is_posted=True)
                new_tweet.save()

    profile = Profile.objects.get(user=user)
    profile.last_sync_time = timezone.now()
    profile.save()


def get_authed_tweepy(access_token, token_secret):
    """Returns an authed instance of the twitter api wrapper tweepy for a given user."""
    social_app_twitter = get_object_or_404(SocialApp, provider='twitter')

    auth = tweepy.OAuthHandler(social_app_twitter.client_id, social_app_twitter.secret)
    auth.set_access_token(access_token, token_secret)
    return tweepy.API(auth)

