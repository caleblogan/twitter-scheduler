from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from allauth.socialaccount.models import SocialToken


@login_required
def index(request):

    print(request.user)
    access_token = get_object_or_404(SocialToken, account__user=request.user, app__provider='twitter')
    print(f'access_token: {access_token}')
    return render(request, 'twitterscheduler/index.html', context={'access_token': access_token})
