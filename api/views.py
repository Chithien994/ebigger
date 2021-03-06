# -*- coding: utf-8 -*-
from django.db.models import Q
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

from core.forms import ChangePasswordForm
from core.utils import get_site_url, iHttpResponse
from api.serializers import UserSerializer, TopicSerializer, VocabularySerializer, FeedbackSerializer
from api.permissions import IsOwnerOrReadOnly
from topics.models import Topic, Vocabulary
from customers.models import Feedback
from verification.models import EmailManager

User = get_user_model()

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
    queryset                = User.objects.none()
    serializer_class        = UserSerializer
    permission_classes      = [IsOwnerOrReadOnly]
    authentication_classes  = [CustomTokenAuthentication,
    						SessionAuthentication, BasicAuthentication]
    filter_backends         = (filters.OrderingFilter,)
    ordering_fields         = '__all__'

    def get_queryset(self):
        try:
            user = self.request.user
            search = self.request.GET.get('search','')
            user_search = 0
            if search.isdigit():
                user_search = int(search)
            qSearch = (
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) | 
                Q(phone_number__icontains=search) | 
                Q(id=user_search))

            if user.is_admin:
                return User.objects.filter(qSearch)
            return User.objects.filter(pk=user.id)
        except Exception as e:
            print(e)
        return User.objects.none()

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
    queryset                = Topic.objects.none()
    serializer_class        = TopicSerializer
    permission_classes      = [IsOwnerOrReadOnly]
    authentication_classes  = [CustomTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    filter_backends         = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields           = ('user',)
    ordering_fields         = '__all__'

    def get_queryset(self):
        try:
            user = self.request.user
            search = self.request.GET.get('search','')
            user_search = 0
            if search.isdigit():
                user_search = int(search)
            qSearch = (Q(name__icontains=search) | Q(user_id=user_search))

            if user.is_admin:
                return Topic.objects.filter(qSearch)
            return Topic.objects.filter(Q(user=user), qSearch)
        except Exception as e:
            print(e)
        return Topic.objects.none()


class VocabularyViewSet(viewsets.ModelViewSet):
    queryset                = Vocabulary.objects.none()
    serializer_class        = VocabularySerializer
    permission_classes      = [IsOwnerOrReadOnly]
    authentication_classes  = [CustomTokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    filter_backends         = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields           = ('topic',)
    ordering_fields         = '__all__'

    def get_queryset(self):
        try:
            user = self.request.user
            search = self.request.GET.get('search','')
            topic_search = 0
            if search.isdigit():
                topic_search = int(search)
            qSearch = (Q(note_source__icontains=search) | Q(note_meaning__icontains=search) | Q(topic_id=topic_search))

            if user and user.is_admin:
                return Vocabulary.objects.filter(qSearch)
            topics = Topic.objects.filter(user=user)
            return Vocabulary.objects.filter(Q(topic__in=topics), qSearch)
        except Exception as e:
            print(e)
        return Vocabulary.objects.none()

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
@permission_classes((IsAuthenticated,))
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