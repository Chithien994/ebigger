from __future__ import absolute_import

import datetime
import hashlib
import os
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.dispatch.dispatcher import receiver
from rest_framework.authtoken.models import Token



def get_file_path(instance, filename):
    """
    :param instance:
    :param filename:
    :return:
    """
    ext = filename.split('.')[-1]
    now = datetime.datetime.now()
    filename = '%s.%s' % (str(hashlib.sha224(str(filename) +
                                             str(now.microsecond)).hexdigest()), ext)
    return os.path.join(instance.directory_string_var, filename)


def photo_upload_to(instance, filename):
    return os.path.join(instance.directory_string_var, str(instance.pk), '%s_profile_picture.jpg'%(instance.phone_number))

def get_thumbnail_path(instance, filename):
    """
    :param instance:
    :param filename:
    :return:
    """
    ext = filename.split('.')[-1]
    now = datetime.datetime.now()
    filename = '%s/%s-%s.%s' % (now.strftime('%Y/%m/%d'),
                                filename.replace('.' + ext, ''), str(now.microsecond), ext)
    return os.path.join(instance.directory_string_var, filename)


@python_2_unicode_compatible
class DateTimeModel(models.Model):
    """
    Abstract model that is used for the model using created and modified fields
    """
    created = models.DateTimeField(
        _('Created'), auto_now_add=True, editable=False)
    modified = models.DateTimeField(
        _('Modified'), auto_now=True, editable=False)

    def __init__(self, *args, **kwargs):
        super(DateTimeModel, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class BiggerUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
        	raise ValueError('Users must have an email address')

        user = self.model(
        	email       = self.normalize_email(email),
        	first_name  = first_name,
        	last_name	= last_name,
        	phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using =self._db)
        return user

    def create_superuser(self, email, first_name, last_name, country_code, phone_number, password):
        """
        Creates and saves a superuser with the given email, phone_number and password.
        """
        user = self.create_user(
        	email,
        	password    = password,
        	first_name  = first_name,
        	last_name	= last_name,
        	phone_number=phone_number,
        )
        user.is_admin   = True
        user.save(using =self._db)
        from verification.models import EmailManager, PhoneManager
        emailManager = EmailManager.objects.create(user=user,email=email,verified=True)
        phoneManager = PhoneManager.objects.create(user=user,country_code=country_code,phone_number=phone_number,verified=True)
        return user

    def create_user_with_facebok(selfs, email, first_name, last_name, birthday, gender, address, facebook_id, facebook_token):

        verified = True
        if not email:
            email = '%s@facebook.com'%(facebook_id)
            verified = False

        user = self.model(
            email       	= self.normalize_email(email),
            first_name  	= first_name,
            last_name		= last_name,
            birthday 		= birthday,
            gender 			= gender,
            address 		= address,
            facebook_id 	= facebook_id,
            facebook_token 	= facebook_token,
        )

        user.set_password(facebook_token)
        user.save(using =self._db)
        from verification.models import EmailManager
        email = EmailManager.objects.create(user=user,email=email,verified=verified)
        return user

class BiggerUser(DateTimeModel, AbstractBaseUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    is_active 		= models.BooleanField(default=True)
    # Permissions
    is_admin 		= models.BooleanField(default=False)
    # Personal info
    email 			= models.EmailField(max_length=80, unique=True)
    first_name 		= models.CharField(max_length=60, blank=True, null=True)
    last_name 		= models.CharField(max_length=60, blank=True, null=True)
    gender 			= models.CharField(max_length=6, choices=GENDER_CHOICES, default='other')
    birthday 		= models.DateField(_('Birthday'), editable=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=photo_upload_to, max_length=255, null=True, blank=True, default='default/avatar-default.jpg')
    phone_number 	= models.CharField(max_length=20, blank=True, null=True)
    company_name 	= models.CharField(null=True, blank=True, max_length=200, default='')
    address 		= models.CharField(null=True, blank=True, max_length=300, default='')
    state 			= models.CharField(null=True, blank=True, max_length=100, default='')
    city 			= models.CharField(null=True, blank=True, max_length=100, default='')
    zip_code 		= models.IntegerField(blank=True, null=True, default=0)
    # Firebase
    firebase_token 	= models.CharField(max_length=250, blank=True, null=True)
    # Facebook
    facebook_id 	= models.CharField(max_length=50, blank=True, null=True)
    facebook_token 	= models.CharField(max_length=250, blank=True, null=True)


    directory_string_var = ''
    objects 		= BiggerUserManager()

    USERNAME_FIELD 	= 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name']

    def __str__(self):
        return '%s [%s]' % (self.email, self.first_name)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin


    def delete(self, *args, **kwargs):
        try:
            if 'default' not in str(self.profile_picture):
                self.profile_picture.delete()
        except:
            pass
        super(BiggerUser, self).delete(*args, **kwargs)

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Bigger Users'


@receiver(models.signals.post_save, sender=BiggerUser)
def create_token(sender, instance, created, **kwargs):
    if created:
        try:
            token, created = Token.objects.get_or_create(user=instance)
        except:
            pass


@receiver(models.signals.pre_save, sender=BiggerUser)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
        Deletes file from filesystem
    """
    if not instance.pk:
        return False
    try:
        old_profile_picture = BiggerUser.objects.get(pk=instance.pk).profile_picture
    except BiggerUser.DoesNotExist:
        return False
    new_profile_picture = instance.profile_picture
    if not old_profile_picture == new_profile_picture and 'default' not in str(instance.profile_picture):
        try:
            old_profile_picture.delete(save=False)
        except:
            pass


class Setting(DateTimeModel):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'settings'