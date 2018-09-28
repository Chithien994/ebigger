from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.dispatch.dispatcher import receiver

from rest_framework import permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import csrf_exempt

from core.utils import iHttpResponse, objectResponse
from verification.models import PhoneManager, EmailManager

User = get_user_model()

def send_sms_verification(user,phone_number, **kwargs):
	print('send_sms_verification: phone %s'%user.phone_number)
	verification = PhoneManager.objects.create(user=user,phone_number=phone_number)
	if verification.send_verification():
		return iHttpResponse(200,'Please check the message, activation code has been sent to your phone number.')
	return iHttpResponse(400,'Error sending verification message!')

def send_email_verification(user,email, **kwargs):
	verification = EmailManager.objects.create(user=user,email=email)
	if verification.send_verification():
		return iHttpResponse(200,'Please check your email for email verification!')
	return iHttpResponse(StatusCode.EMAIL_ADDRESS_IS_INVALID.value,
		MESSAGES[StatusCode.EMAIL_ADDRESS_IS_INVALID])

class ResendView(generics.GenericAPIView):

	@api_view(['POST'])
	@csrf_exempt
	@permission_classes((permissions.AllowAny,))
	def resend_or_create(self):
	    phone = self.request.data.get('phone')
	    send_new = self.request.data.get('new')
	    sms_verification = None

	    user = User.objects.filter(phone_number=phone).first()

	    if not send_new:
	        sms_verification = SMSVerification.objects.filter(user=user, verified=False) \
	            .order_by('-created_at').first()

	    if sms_verification is None:
	        sms_verification = PhoneManager.objects.create(user=user, phone=phone)

	    return sms_verification.send_verification()

	def post(self, request, *args, **kwargs):
	    success = self.resend_or_create()

	    return Response(dict(success=success), status=status.HTTP_200_OK)
