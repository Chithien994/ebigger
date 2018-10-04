# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import permission_classes
from rest_framework import exceptions, filters, viewsets, permissions
from rest_framework.authentication import BasicAuthentication, \
    SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics

from core.forms import ChangePasswordForm
from core.utils import get_site_url
from api.serializers import UserSerializer, TopicSerializer, VocabularySerializer, FeedbackSerializer
from topics.models import Topic, Vocabulary
from customers.models import Feedback
from verification.models import EmailManager

User = get_user_model()

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        print('BasePermission: ',str(request.method))
        if request.method in permissions.SAFE_METHODS:
            return True
        # Instance must have an attribute named `owner`.

        obj_user_id = None
        my_user_id =request.user.id
        try:
        	obj_user_id = obj.user_id
        except Exception as e:
        	obj_user_id = obj.id
        
        if obj_user_id == my_user_id:
        	return True

        user = User.objects.get(pk=my_user_id)
        if user and user.is_admin:
        	return True
        return False

class CustomTokenAuthentication(TokenAuthentication):
    model = Token
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)
		

class UserViewSet(viewsets.ModelViewSet):
	queryset                = User.objects.all()
	serializer_class        = UserSerializer
	permission_classes      = [IsOwnerOrReadOnly]
	authentication_classes  = [CustomTokenAuthentication,
							SessionAuthentication, BasicAuthentication]
	filter_backends         = (filters.OrderingFilter,)
	ordering_fields         = '__all__'


def reset_password(request, uidb64, token):
    user_id = urlsafe_base64_decode(uidb64)
    user    = User.objects.get(pk=user_id)
    password_change_form = ChangePasswordForm()
    msg     = ''
    if not user:
        return render(request, 'frontend/reset_password_invalid.html', {})

    math = default_token_generator.check_token(user, token)
    if not math:
        return render(request, 'frontend/reset_password_invalid.html', {})
    if request.method == 'POST':
        password_change_form = ChangePasswordForm(request.POST)
        if password_change_form.is_valid():
            password = request.POST.get('password', '').strip()
            if user:
                math = default_token_generator.check_token(user, token)
                if math:
                    user.set_password(password)
                    user.save()
                    return render(request, 'frontend/reset_password_successfully.html', {})

    return render(request, 'frontend/reset_password.html',
                  {'uidb64': uidb64, 'token': token, 'msg': msg, 'password_change_form': password_change_form})

def verify_email(request, uidb64, token):
    user_id = urlsafe_base64_decode(uidb64)
    user    = User.objects.get(pk=user_id)
    msg     = ''
    if not user:
        return render(request, 'frontend/email/verify_email_invalid.html', {})
    math = default_token_generator.check_token(user, token)
    if not math:
        return render(request, 'frontend/email/verify_email_invalid.html', {})
    email = EmailManager.objects.get(user=user)
    if email.verified:
        return render(request, 'frontend/email/verify_email_invalid.html', {})
    email.verified = True
    email.save()
    return render(request, 'frontend/email/verify_email_successfully.html', {})

class TopicViewSet(viewsets.ModelViewSet):
    queryset                = Topic.objects.all()
    serializer_class        = TopicSerializer
    permission_classes      = [IsOwnerOrReadOnly]
    authentication_classes  = [CustomTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    filter_backends         = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields           = ('user',)
    ordering_fields         = '__all__'


class VocabularyViewSet(viewsets.ModelViewSet):
    queryset                = Vocabulary.objects.all()
    serializer_class        = VocabularySerializer
    permission_classes      = [IsOwnerOrReadOnly]
    authentication_classes  = [CustomTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    filter_backends         = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields           = ('topic',)
    ordering_fields         = '__all__'

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset                = Feedback.objects.all()
    serializer_class        = FeedbackSerializer
    permission_classes      = [IsAdminUser]
    authentication_classes  = [CustomTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    filter_backends         = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields           = ('user',)
    ordering_fields         = '__all__'

@csrf_exempt
@permission_classes((permissions.IsAuthenticated,))
def oauth2callback(request):
    from oauth2client import client
    if not request.user.is_superuser:
        return redirect(reverse('home'))
    scopes = [
        'https://www.googleapis.com/auth/androidpublisher'
    ]
    flow = client.flow_from_clientsecrets(
        settings.CLIENT_SECRET,
        scope       = ','.join(scopes),
        redirect_uri=get_site_url() + reverse('oauth2callback'))
    flow.params['include_granted_scopes'] = 'true'
    flow.params['approval_prompt'] = 'force'
    flow.params['access_type'] = 'offline'
    try:
        auth_uri = flow.step1_get_authorize_url()
        if request.GET.get('code'):
            auth_code   = request.GET.get('code')
            credentials = flow.step2_exchange(auth_code)
            with open(settings.CLIENT_DATA, 'w') as f:
                print('credentials', credentials.to_json())
                f.write(credentials.to_json())
            return redirect(reverse('home'))
        return redirect(auth_uri)
    except:
        return redirect(reverse('home'))