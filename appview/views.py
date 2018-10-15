from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from social_django.models import UserSocialAuth

def home(request):
    return render(request, 'frontend/home.html',{})

@login_required
def settings(request):
    user = request.user
    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'frontend/settings.html', {
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })