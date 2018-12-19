import facebook

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext as _
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import csrf_exempt
from rest_framework.authtoken.models import Token

from api.serializers import NewUserSerializer
from core.enums import StatusCode
from core.constants import MESSAGES
from core.utils import get_site_url, is_email, \
    send_email, validate_user_data, iHttpResponse, objectResponse
from apps.models import AppInfo
from verification.views import send_sms_verification, send_email_verification
from verification.models import EmailManager, PhoneManager
from verification.verification import checkCode

User = get_user_model()

def userResponse(user):
  	return objectResponse(NewUserSerializer(user).data)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def confirm_sms_verification(request):
    """
    Phone number verification to complete registration
    With body: 
    {
        "phone_number":"string",
        "verify_code":"string"
    }
    """
    phone_number    = request.data.get('phone_number')
    code            = request.data.get('verify_code')
    if phone_number:
        phoneManager = PhoneManager.objects.filter(phone_number=phone_number, verified=False).first()
        if phoneManager and checkCode(phoneManager.country_code, phone_number, code):
            phoneManager.verified = True
            phoneManager.save()
            user = User.objects.filter(pk=phoneManager.user_id).first()
            return userResponse(user)
    return iHttpResponse('401','Failure')

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def resend_verification_message(request):
    """Resend verification message
    With body: 
    {
        "phone_number":"string"
    }
    """
    phone_number    = request.data.get('phone_number')
    phoneManager    = PhoneManager.objects.filter(phone_number=phone_number, verified=False).first()
    if phoneManager and phoneManager.send_verification():
        return iHttpResponse(200,'Verification code has been sent to your phone number.')
    return iHttpResponse(400,'Error sending verification message!')

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def signup(request):
	"""
	Signup new user
    With body: 
    {
        "country_code":"string",
        "phone_number":"string",
        "email":"string",
        "password":"string",
        "first_name":"string",
        "last_name":"string"
    }
	"""
	email           = request.data.get('email')
	password        = request.data.get('password')
	country_code    = request.data.get('country_code')
	phone_number    = request.data.get('phone_number')
	first_name      = request.data.get('first_name')
	last_name       = request.data.get('last_name')
	code, message   = validate_user_data(request.data)
	if code and message:
		return iHttpResponse(code, message)
	emailManager = EmailManager.objects.filter(email=email).first()
	if emailManager and emailManager.verified:
		return iHttpResponse(StatusCode.EMAIL_ADDRESS_IS_EXISTS.value,
		    MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EXISTS])

	phoneManager = PhoneManager.objects.filter(phone_number=phone_number).first()
	if not phoneManager:
		user = User.objects.create_user(email, first_name, last_name, phone_number, password)
		send_email_verification(user,email)
		return send_sms_verification(user,country_code,phone_number)

	elif not phoneManager.verified:
		user = User.objects.filter(pk=phoneManager.user_id).first()
		user.email = email
		user.phone_number = phone_number
		user.first_name = first_name
		user.last_name = last_name
		user.set_password(password)
		user.save()
		send_email_verification(user,email)
		return send_sms_verification(user,country_code,phone_number)

	return iHttpResponse(400, 'This phone number already exists in our system')


@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def login(request):
	"""
	Login
    With body: 
    {
        "username":"string",
        "password":"string"
    }
	"""
	username = request.data.get('username')
	password = request.data.get('password')

	emailManager = EmailManager.objects.filter(email=username).first()
	if emailManager and emailManager.verified:
		return check_password(emailManager.user_id, password)

	phoneManager = PhoneManager.objects.filter(phone_number=username).first()
	if phoneManager and phoneManager.verified:
		return check_password(phoneManager.user_id, password)   

	return iHttpResponse(StatusCode.USERNAME_IS_INVALID.value,
			MESSAGES[StatusCode.USERNAME_IS_INVALID])

def check_password(user_id, password):
	user = User.objects.get(pk=user_id)
	if user.check_password(password):
		return userResponse(user)
	else:
		return iHttpResponse(StatusCode.PASSWORD_IS_INVALID.value,
			MESSAGES[StatusCode.PASSWORD_IS_INVALID])

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def authfacebook(request):
    """
    Function for login and register with facebook
    With body: 
    {
        "access_token":"string"
    }
    """
    # data = json.loads(request.body.decode('utf-8'))
    access_token 	= request.data.get('access_token')
    facebook_id 	= ''
    email 			= ''
    try:
    	graph = facebook.GraphAPI(access_token=access_token)
    	user_info = graph.get_object(
    	    id='me',
    	    fields='first_name, middle_name, last_name, id, '
    	    'currency, hometown, location, locale, '
    	    'email, gender, interested_in, picture.type(large),'
    	    ' birthday, cover')
    	facebook_id = user_info.get('id')
    	email 		= user_info.get('email')
    except facebook.GraphAPIError:
    	return iHttpResponse(StatusCode.ACCESS_TOKEN_FB_IS_INVALID.value,
    		MESSAGES[StatusCode.ACCESS_TOKEN_FB_IS_INVALID])

    user = User.objects.get(email=email)
    if user and EmailManager.objects.get(user=user).verified:
    	user.facebook_id       = facebook_id
    	user.facebook_token    = access_token
    	user.save()
    	return userResponse(user)
    user = User.objects.get(facebook_id=facebook_id)
    if user:
        user.facebook_token = access_token
        user.email          = email
        user.save()  
        return userResponse(user)

    user = User.objects.create_user_with_facebok(
    	email, 
    	user_info.get('first_name'), 
    	user_info.get('last_name'), 
    	user_info.get('birthday'), 
    	user_info.get('gender'), 
    	user_info.get('location')['name'], 
    	facebook_id, 
    	access_token)
    return userResponse(user)



@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def forgotpassword(request):
    """
    forgot password
    With body: 
    {
        "email":"string"
    }
    """
    print('forgotpassword', settings.EMAIL_HOST_PASSWORD, settings.EMAIL_HOST_USER)
    SITE_URL = get_site_url()
    email_address = request.data.get('email')
    code, message = None, None
    if not email_address:
        code = StatusCode.EMAIL_ADDRESS_IS_EMPTY.value
        message = MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EMPTY]
    elif email_address and not is_email(email_address):
        code = StatusCode.EMAIL_ADDRESS_IS_INVALID.value
        message = MESSAGES[StatusCode.EMAIL_ADDRESS_IS_INVALID]
    else:
        if User.objects.filter(email=email_address).exists():
            user = User.objects.get(email=email_address)
            subject = "Password Reset"
            message_html = "email/reset_password.html"
            email_from = ""
            email_to = [user.email]

            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            obj_model = {
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'reset_pass_url': SITE_URL + reverse('resetpassword',
                                                     kwargs={'uidb64': str(uidb64, 'utf-8'), 'token': token})
            }
            print('reset_pass_url', obj_model['reset_pass_url'])
            send_email(subject, message_html, email_from, email_to, obj_model)
            code = 200
            message = _('Please check your email to get the new password!')
        else:
            code = StatusCode.EMAIL_ADDRESS_IS_INVALID.value
            message = MESSAGES[StatusCode.EMAIL_ADDRESS_IS_INVALID]
    return iHttpResponse(code, message)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.IsAuthenticated,))
def changepassword(request):
    """
    change password
    With body: 
    {
        "old_password":"string",
        "new_password":"string"
    }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    code, message = None, None
    if not old_password or not user.check_password(old_password):
        code = StatusCode.OLD_PASSWORD_IS_INVALID.value
        message = MESSAGES[StatusCode.OLD_PASSWORD_IS_INVALID]
    elif not new_password:
        code = StatusCode.NEW_PASSWORD_IS_INVALID.value
        message = MESSAGES[StatusCode.NEW_PASSWORD_IS_INVALID]
    else:
        code, message = 200, _('Your password has been changed successfully!')
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        obj = "{'code': code, 'message': message, 'token': token.key}"
        return objectResponse(obj)
    return iHttpResponse(code, message)

@api_view(['GET'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def check_app_info(request):
    """
    check app info
    """
    appinfo_list = {}
    for appinfo in AppInfo.objects.all():
        appinfo_list[appinfo.key] = appinfo.value
    return objectResponse(appinfo_list)

@api_view(['GET'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def setting(request):
    """
    check app info
    """
    setting_list = {}
    for setting in Setting.objects.all():
        setting_list[setting.key] = setting.value
    return objectResponse(setting_list)