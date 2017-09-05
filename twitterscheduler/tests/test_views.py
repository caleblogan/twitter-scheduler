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
import twitterscheduler.tasks


class TestIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

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


class TestCreateScheduledTweet(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('test_user1', password='nice_pass')
        self.user2 = User.objects.create_user('test_user2', password='nice_pass')
        self.view_reverse = reverse('twitterscheduler:create-scheduled-tweet')

    def test_exists_at_desired_url(self):
        resp = self.client.get('/scheduler/tweet/create/')
        self.assertNotEqual(resp.status_code, 404)

    def test_reverse_url(self):
        resp = self.client.get(self.view_reverse)
        self.assertNotEqual(resp.status_code, 404)

    def test_redirected_to_login_if_not_authed(self):
        resp = self.client.get(self.view_reverse)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, f'/accounts/login/?next={self.view_reverse}')

    def test_logged_in_user_can_access_page(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        self.assertEqual(resp.status_code, 200)

    def test_tweet_form_in_context(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        self.assertTrue('tweet_form' in resp.context)

    def test_correct_template(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        self.assertTemplateUsed(resp, 'twitterscheduler/create_scheduled_tweet.html')

    def test_form_correct_initial_date(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.view_reverse)
        future_date = timezone.now() + datetime.timedelta(minutes=5)
        self.assertTrue(future_date - resp.context['tweet_form'].initial['time_to_tweet'] < datetime.timedelta(seconds=10))

    @mock.patch('twitterscheduler.views.tweet_task', auto_spec=True)
    def test_redirects_to_index_after_posting_valid_data(self, task_mock):
        login = self.client.login(username='test_user1', password='nice_pass')
        time_to_tweet = datetime.datetime.now()+datetime.timedelta(minutes=5)
        resp = self.client.post(self.view_reverse, {'time_to_tweet': time_to_tweet, 'text': 'nice tweet dood'})
        self.assertRedirects(resp, reverse('twitterscheduler:index'))

    @mock.patch('twitterscheduler.views.tweet_task', autospec=True)
    def test_adds_tweet_and_scheduled_tweet_to_db(self, task_mock):
        tweets = Tweet.objects.filter(text='nice tweet dood')
        self.assertEqual(len(tweets), 0)

        login = self.client.login(username='test_user1', password='nice_pass')
        time_to_tweet = datetime.datetime.now()+datetime.timedelta(minutes=5)
        resp = self.client.post(self.view_reverse, {'time_to_tweet': time_to_tweet, 'text': 'nice tweet dood'})
        tweets = Tweet.objects.filter(text='nice tweet dood')
        scheduled_tweets = ScheduledTweet.objects.filter(tweet=tweets[0])
        self.assertEqual(len(tweets), 1)
        self.assertEqual(len(scheduled_tweets), 1)

    @mock.patch('twitterscheduler.views.tweet_task', autospec=True)
    def test_tweet_task_is_called_correctly(self, task_mock):
        login = self.client.login(username='test_user1', password='nice_pass')
        time_to_tweet = datetime.datetime.now()+datetime.timedelta(minutes=5)
        resp = self.client.post(self.view_reverse, {'time_to_tweet': time_to_tweet, 'text': 'nice tweet dood'})

        task_mock.apply_async.assert_called()
        scheduled_tweet = ScheduledTweet.objects.get(tweet__text='nice tweet dood')
        task_mock.apply_async.assert_called_with(('test_user1', scheduled_tweet.id), eta=scheduled_tweet.time_to_tweet)


class TestEditScheduledTweet(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('test_user1', password='nice_pass')
        self.user2 = User.objects.create_user('test_user2', password='nice_pass')
        self.tweet = Tweet.objects.create(user=self.user1, text='nice tweet')
        self.scheduled_tweet = ScheduledTweet.objects.create(
            tweet=self.tweet,
            time_to_tweet=timezone.now()+datetime.timedelta(minutes=15)
        )

    def test_exists_at_desired_url(self):
        resp = self.client.get(f'/scheduler/scheduled-tweet/{self.scheduled_tweet.id}/edit/')
        self.assertNotEqual(resp.status_code, 404)

    def test_redirected_to_login_if_not_authed(self):
        resp = self.client.get(self.scheduled_tweet.get_absolute_url())
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, f'/accounts/login/?next={self.scheduled_tweet.get_absolute_url()}')

    def test_logged_in_user_can_access_page(self):
        login = self.client.login(username='test_user1', password='nice_pass')
        resp = self.client.get(self.scheduled_tweet.get_absolute_url())
        self.assertEqual(resp.status_code, 200)

    def test_404_if_scheduled_tweet_doesnt_belong_to_user(self):
        login = self.client.login(username='test_user2', password='nice_pass')
        resp = self.client.get(self.scheduled_tweet.get_absolute_url())
        self.assertEqual(resp.status_code, 404)

    def test_updates_scheduled_tweet_with_valid_data(self):
        import pytz
        timezone = pytz.timezone("America/Los_Angeles")
        login = self.client.login(username='test_user1', password='nice_pass')
        time_to_tweet = datetime.datetime.now() + datetime.timedelta(minutes=5)
        resp = self.client.post(
            self.scheduled_tweet.get_absolute_url(),
            {'time_to_tweet': time_to_tweet, 'text': 'boondocks'}
        )
        scheduled_tweet = ScheduledTweet.objects.get(pk=self.scheduled_tweet.id)
        self.assertEqual(scheduled_tweet.tweet.text, 'boondocks')
        self.assertEqual(scheduled_tweet.time_to_tweet, timezone.localize(time_to_tweet))
