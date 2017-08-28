from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.http import Http404
from django.contrib.sites.models import Site

import datetime
from unittest import mock

from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken

from twitterscheduler.models import Tweet, ScheduledTweet, Profile


class TestIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 tweets
        user = User.objects.create_user('boy', password='nice_pass')
        num_tweets = 13
        for tweet_i in range(num_tweets):
            Tweet.objects.create(tweet_id=str(tweet_i), text=f'text for tweet_i: {tweet_i}', user=user, sentiment='p',
                                 is_posted=True, time_posted_at=timezone.now()+datetime.timedelta(minutes=-tweet_i))

    def setUp(self):
        self.user1 = User.objects.create_user('test_user1', password='nice_pass')
        self.user2 = User.objects.create_user('test_user2', password='nice_pass')
        self.view_reverse = reverse('twitterscheduler:index')

    def test_exists_at_desired_url(self):
        resp = self.client.get('/scheduler/')
        self.assertNotEqual(resp.status_code, 404)

    def test_redirects_when_not_logged_in(self):
        resp = self.client.get(self.view_reverse)
        self.assertRedirects(resp, f'/accounts/login/?next={self.view_reverse}')

    def test_accessible_when_logged_in(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        self.assertEqual(resp.status_code, 200)

    def test_correct_user_context(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        self.assertEqual(str(resp.context['user']), 'test_user1')

    def test_correct_template(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        self.assertTemplateUsed(resp, 'twitterscheduler/index.html')

    def test_user_tweets_context_is_passed_in(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)

        self.assertTrue('user_tweets' in resp.context)
        self.assertEqual(len(resp.context['user_tweets']), 0)

        Tweet.objects.create(user=self.user1, text='text 1')
        Tweet.objects.create(user=self.user1, text='text 2')
        resp = self.client.get(self.view_reverse)
        self.assertEqual(len(resp.context['user_tweets']), 2)

    def test_only_users_tweets_are_in_context(self):
        login = self.client.login(username='test_user1', password='nice_pass')

        Tweet.objects.create(user=self.user1, text='text 1')
        Tweet.objects.create(user=self.user1, text='text 2')
        Tweet.objects.create(user=self.user2, text='text 3')
        resp = self.client.get(self.view_reverse)
        self.assertEqual(len(resp.context['user_tweets']), 2)
        for tweet in resp.context['user_tweets']:
            self.assertEqual(tweet.user.username, 'test_user1')
