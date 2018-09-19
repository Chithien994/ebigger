from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from core.constants import VALIDATION_CODE
from core.enums import ValidationStatusCode
from topics.models import Topic, Vocabulary
from customers.models import Feedback
from apps.models import AppInfo


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    def get_email(self, obj):
        return obj.email
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'created', 'modified', 'is_active', 'is_admin')

    def to_internal_value(self, data):
        full_name = data.get('full_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        if data.get('is_admin'):
            data['is_admin'] = False
        if data.get('password'):
            raise serializers.ValidationError(
                {'message': VALIDATION_CODE[ValidationStatusCode.NEW_PASSWORD_IS_INVALID], 'code': ValidationStatusCode.NEW_PASSWORD_IS_INVALID.value})
        if not phone_number:
            raise serializers.ValidationError(
                {'message': VALIDATION_CODE[ValidationStatusCode.PHONE_NUMBER_IS_INVALID], 'code': ValidationStatusCode.PHONE_NUMBER_IS_INVALID.value})
        if not full_name:
            raise serializers.ValidationError(
                {'message': VALIDATION_CODE[ValidationStatusCode.FULL_NAME_IS_EMPTY], 'code': ValidationStatusCode.FULL_NAME_IS_EMPTY.value})
        elif not email:
            raise serializers.ValidationError(
                {'message': VALIDATION_CODE[ValidationStatusCode.EMAIL_ADDRESS_IS_EMPTY], 'code': ValidationStatusCode.EMAIL_ADDRESS_IS_EMPTY.value})
        data['email'] = email
        return data


class NewUserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def get_email(self, obj):
        return obj.email

    class Meta:
        model   = User
        exclude = ('password', 'is_active', 'last_login','created', 'modified', 'is_admin')
            
class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model 	= Topic
		fields 	= '__all__'

class VocabularySerializer(serializers.ModelSerializer):
	class Meta:
		model 	= Vocabulary
		fields 	= '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
	class Meta:
		model 	= Feedback
		fields 	= '__all__'

class AppInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model   = AppInfo
        fields  = '__all__'