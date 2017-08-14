from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from allauth.socialaccount.models import SocialToken, SocialApp

import tweepy


@login_required
def index(request):
    access_token = get_object_or_404(SocialToken, account__user=request.user, app__provider='twitter')
    # token, token_secret = access_token.token, access_token.token_secret
    print(f'user: {request.user}')
    print(f'access_token: {access_token.token}')


    context = {
        'access_token': access_token,
        # 'user_tweets': user_tweets,
    }

    return render(request, 'twitterscheduler/index.html', context=context)


def sync_tweets_twitter(access_token, token_secret):
    """Gets the users tweets from twitter and saves them to db."""
    twitter_api = get_authed_tweepy(access_token, token_secret)

    public_tweets = twitter_api.user_timeline()
    if public_tweets:
        return JsonResponse({'tweet': public_tweets[0]._json})


def get_authed_tweepy(access_token, token_scret):
    """Returns an authed instance of the twitter api wrapper tweepy for a given user."""
    social_app_twitter = get_object_or_404(SocialApp, provider='twitter')

    auth = tweepy.OAuthHandler(social_app_twitter.client_id, social_app_twitter.secret)
    auth.set_access_token(access_token, token_scret)
    return tweepy.API(auth)
