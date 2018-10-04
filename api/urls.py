from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from api import v1
from api.views import UserViewSet, TopicViewSet, VocabularyViewSet, FeedbackViewSet

app_name = 'api'
api_v1 = DefaultRouter()
api_v1.register(r'users', UserViewSet)
api_v1.register(r'topics', TopicViewSet)
api_v1.register(r'vocabularys', VocabularyViewSet)
api_v1.register(r'feedbacks', FeedbackViewSet)

urlpatterns = [
	url(r'v1/', include((api_v1.urls, 'api_v1'), namespace='ebigger')),
	url(r'v1/signup', v1.signup, name='signup'),
	url(r'v1/login', v1.login, name='login'),
	url(r'v1/forgotpassword', v1.forgotpassword, name='forgotpassword'),
	url(r'v1/changepassword', v1.changepassword, name='changepassword'),
	url(r'v1/appinfo', v1.check_app_info, name='check_app_info'),
	url(r'v1/authfacebook', v1.authfacebook, name='authfacebook'),
	url(r'v1/smsverification', v1.confirm_sms_verification, name='smsverification'),
	url(r'v1/resendsms', v1.resend_verification_message, name='resendsms'),
]