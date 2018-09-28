import json
import facebook

from django.http import HttpResponse, JsonResponse
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
from core.utils import get_site_url, is_email, is_mobile, \
    send_email, validate_user_data, iHttpResponse, objectResponse
from apps.models import AppInfo
from verification.views import send_sms_verification, send_email_verification
from verification.models import EmailManager

User = get_user_model()

def userResponse(user):
  	return objectResponse(NewUserSerializer(user).data)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def confirm_sms_verification():
    return iHttpResponse('200','Successfully')

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def signup(request):
    """
    Signup new user
    """
    email           = request.data.get('email')
    password        = request.data.get('password')
    phone_number    = request.data.get('phone_number')
    first_name      = request.data.get('first_name')
    last_name       = request.data.get('last_name')
    code, message   = validate_user_data(request.data)
    if code and message:
    	return iHttpResponse(code, message)
    user = User.objects.get(email=email)
    if user and Manager.objects.get(user=user).verified:
    	return iHttpResponse(StatusCode.EMAIL_ADDRESS_IS_EXISTS.value,
            MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EXISTS])

    if not User.objects.filter(phone_number=phone_number).exists():
        user = User.objects.create_user(email, first_name, last_name, phone_number, password)
        send_sms_verification(user,phone_number)
        return send_email_verification(user,email)

    return iHttpResponse(400, 'This phone number already exists in our system')


@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def login(request):
    """
    Login
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = User.objects.get(email=username)
    if user and EmailManager.objects.get(user=user).verified:
    	return check_password(user, password)

    if User.objects.filter(phone_number=username).exists():
    	user = User.objects.get(phone_number=username)
    	return check_password(user, password)   

    return iHttpResponse(StatusCode.USERNAME_IS_INVALID.value,
    		MESSAGES[StatusCode.USERNAME_IS_INVALID])

def check_password(user, password):
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
    """
    # data = json.loads(request.body.decode('utf-8'))
    access_token 	= request.data.get('access_token')
    facebook_id 	= ''
    email 			= '';
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