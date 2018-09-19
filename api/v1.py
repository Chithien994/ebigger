import json

from django.http import HttpResponse
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

from api.serializers import NewUserSerializer
from core.enums import ValidationStatusCode
from core.constants import VALIDATION_CODE
from core.utils import get_site_url, is_email, is_mobile, \
    send_email, validate_user_data
from apps.models import AppInfo

User = get_user_model()

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def signup(request):
    """
    Signup new user
    """
    email = request.data.get('email')
    password = request.data.get('password')
    phone_number = request.data.get('phone_number')
    full_name = request.data.get('full_name')
    code, message = validate_user_data(request.data)
    if code and message:
        return HttpResponse(json.dumps({'code': code, 'message': message}),
                            content_type='application/json',
                            status=200)
    if User.objects.filter(email=email).exists():
        return HttpResponse(json.dumps({'code': 400, 'message': _('This email already exists in our system')}),
                            content_type='application/json',
                            status=200)
    if not User.objects.filter(phone_number=phone_number).exists():
        user = User.objects.create_user(
            email, full_name, phone_number, password)
        return HttpResponse(json.dumps(NewUserSerializer(user).data),
                            content_type='application/json',
                            status=200)
    return HttpResponse(json.dumps({'code': 400, 'message': _('This phone number already exists in our system')}),
                        content_type='application/json',
                        status=200)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def login(request):
    """
    Login
    """
    phone_number = request.data.get('phone_number')
    if User.objects.filter(phone_number=phone_number).exists():
        password = request.data.get('password')
        user = User.objects.get(phone_number=phone_number)
        if user.check_password(password):
            return HttpResponse(json.dumps(NewUserSerializer(user).data),
                                content_type='application/json',
                                status=200)
        else:
            return HttpResponse(json.dumps({'code': ValidationStatusCode.PASSWORD_IS_INVALID.value, 'message': VALIDATION_CODE[ValidationStatusCode.PASSWORD_IS_INVALID]}),
                                content_type='application/json',
                                status=200)
    else:
        return HttpResponse(json.dumps({'code': ValidationStatusCode.PHONE_NUMBER_IS_INVALID.value, 'message': VALIDATION_CODE[ValidationStatusCode.PHONE_NUMBER_IS_INVALID]}),
                            content_type='application/json',
                            status=200)


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
        code = ValidationStatusCode.EMAIL_ADDRESS_IS_EMPTY.value
        message = VALIDATION_CODE[ValidationStatusCode.EMAIL_ADDRESS_IS_EMPTY]
    elif email_address and not is_email(email_address):
        code = ValidationStatusCode.EMAIL_ADDRESS_IS_INVALID.value
        message = VALIDATION_CODE[ValidationStatusCode.EMAIL_ADDRESS_IS_INVALID]
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
            code = ValidationStatusCode.EMAIL_ADDRESS_IS_INVALID.value
            message = VALIDATION_CODE[ValidationStatusCode.EMAIL_ADDRESS_IS_INVALID]
    return HttpResponse(json.dumps({'code': code, 'message': message}),
                        content_type='application/json',
                        status=200)

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
        code = ValidationStatusCode.OLD_PASSWORD_IS_INVALID.value
        message = VALIDATION_CODE[ValidationStatusCode.OLD_PASSWORD_IS_INVALID]
    elif not new_password:
        code = ValidationStatusCode.NEW_PASSWORD_IS_INVALID.value
        message = VALIDATION_CODE[ValidationStatusCode.NEW_PASSWORD_IS_INVALID]
    else:
        code, message = 200, _('Your password has been changed successfully!')
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return HttpResponse(json.dumps({'code': code, 'message': message, 'token': token.key}),
                            content_type='application/json',
                            status=200)
    return HttpResponse(json.dumps({'code': code, 'message': message}),
                        content_type='application/json',
                        status=200)

@api_view(['GET'])
@csrf_exempt
def check_app_info(request):
    """
    check_app_info
    """
    appinfo_list = {}
    for appinfo in AppInfo.objects.all():
        appinfo_list[appinfo.key] = appinfo.value
    return HttpResponse(json.dumps(appinfo_list),
                        content_type='application/json',
                        status=200)