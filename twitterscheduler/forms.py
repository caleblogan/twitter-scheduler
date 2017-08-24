from django import forms

from .models import ScheduledTweet, Tweet


class CreateScheduleTweetForm(forms.Form):
    time_to_tweet = forms.DateTimeField()
    text = forms.CharField(max_length=140, widget=forms.Textarea)

