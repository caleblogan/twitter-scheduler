import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import reverse


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    require_correctly_spelled = models.BooleanField(default=False)
    require_positive_sentiment = models.BooleanField(default=False)
    last_sync_time = models.DateTimeField(default=timezone.now()-datetime.timedelta(minutes=30))

    SYNC_THRESHOLD = datetime.timedelta(minutes=15)

    def synced_tweets_recently(self):
        return timezone.now() - self.last_sync_time < self.SYNC_THRESHOLD

    def __str__(self):
        return f'{self.user} ({self.last_sync_time})'


class Tweet(models.Model):
    tweet_id = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=140)

    sentiment_choices = (
        ('p', 'positive'),
        ('n', 'negative'),
        ('u', 'unknown')
    )
    sentiment = models.CharField(max_length=1, choices=sentiment_choices, blank=True, default='u',
                                 help_text='Sentiment of tweet')
    time_posted_at = models.DateTimeField(null=True, blank=True)
    is_posted = models.BooleanField(default=False, help_text='Whether or not the tweet has been posted to twitter')

    class Meta:
        ordering = ['-time_posted_at']

    def __str__(self):
        return f'{self.user} - {self.text}'


class ScheduledTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    time_to_tweet = models.DateTimeField()
    task_id = models.CharField(max_length=36, null=True, blank=True)

    class Meta:
        ordering = ['time_to_tweet']

    def get_absolute_url(self):
        return reverse('twitterscheduler:edit-scheduled-tweet', args=[str(self.id)])

    def __str__(self):
        return f'{self.tweet} ({self.time_to_tweet})'
