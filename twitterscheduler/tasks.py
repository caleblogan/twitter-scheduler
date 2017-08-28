from django.contrib.auth.models import User

from allauth.socialaccount.models import SocialToken, SocialApp

from .models import ScheduledTweet

from celery import shared_task
import tweepy


@shared_task
def add_task(x, y, out_format='int'):
    return eval(out_format)(x + y)


@shared_task
def tweet_task(username, scheduled_tweet_id):
    user = User.objects.get(username=username)
    access_token = SocialToken.objects.get(account__user=user, app__provider='twitter')
    twitter = get_authed_tweepy(access_token.token, access_token.token_secret)
    scheduled_tweet = ScheduledTweet.objects.get(id=scheduled_tweet_id)

    twitter.update_status(status=scheduled_tweet.tweet.text)

    return f'sent tweet for user {user} - {scheduled_tweet.tweet.text}'


def get_authed_tweepy(access_token, token_secret):
    """Returns an authed instance of the twitter api wrapper tweepy for a given user."""
    social_app_twitter = SocialApp.objects.get(provider='twitter')

    auth = tweepy.OAuthHandler(social_app_twitter.client_id, social_app_twitter.secret)
    auth.set_access_token(access_token, token_secret)
    return tweepy.API(auth)

