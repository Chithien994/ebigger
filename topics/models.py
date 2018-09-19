import os
import datetime

from datetime import date, time

from random import randint
from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

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
    return os.path.join(instance.directory_string_var, 'topics/%s'%str(instance.user.pk), '%s.jpg'%str(instance.created.now().strftime('%d%m%Y%H%M%S')))

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
class Privileged(models.Model):
	"""docstring for privileged"""
	key = models.IntegerField(validators=[MaxValueValidator(3), MinValueValidator(1)], blank=True, unique=True)
	name = models.CharField(max_length=20, blank=False)

	def __str__(self):
		return 'Shared with: %s' % self.name

	class Meta:
		db_table = 'privilegeds'


@python_2_unicode_compatible
class DateTimeModel(models.Model):
    """
    Abstract model that is used for the model using created and modified fields
    """
    created = models.DateTimeField(
        _('Created'), auto_now_add=True, editable=False)
    last_action = models.DateTimeField(
        _('Last Action'), auto_now_add=True, editable=False)
    modified = models.DateTimeField(
        _('Modified'), auto_now=True, editable=False)

    def __init__(self, *args, **kwargs):
        super(DateTimeModel, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True
		

@python_2_unicode_compatible
class Topic(DateTimeModel):
    user			= models.ForeignKey(get_user_model(), related_name='topics', on_delete=models.CASCADE)
    privileged  	= models.ForeignKey(Privileged, related_name='privileged_topic', on_delete=models.CASCADE)
    name			= models.CharField(max_length=80, blank=True, null=True)
    picture 		= models.ImageField(upload_to=photo_upload_to, max_length=255, null=True, blank=True, default='topics/default/avatar-default.jpg')
    directory_string_var = ''
    def __str__(self):
        return 'Topic #%s-%s' % (self.pk, self.name)

    def delete(self, *args, **kwargs):
        try:
            self.picture.delete()
        except:
            pass
        super(Topic, self).delete(*args, **kwargs)

    class Meta:
        db_table 			= 'topics'
        verbose_name_plural = 'Topics'

@receiver(models.signals.pre_save, sender=Topic)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
        Deletes file from filesystem
    """
    if not instance.pk:
        return False
    try:
        old_picture = Topic.objects.get(pk=instance.pk).picture
    except Topic.DoesNotExist:
        return False
    new_picture = instance.picture
    if not old_picture == new_picture:
        try:
            old_picture.delete(save=False)
        except:
            pass

@python_2_unicode_compatible
class Vocabulary(DateTimeModel):
	"""docstring for vocabulary"""
	topic		    	= models.ForeignKey(Topic, related_name='vocabularys', on_delete=models.CASCADE)
	note_source			= models.TextField(default='', blank=True, null=True)
	langguage_source	= models.CharField(max_length=80, blank=True, null=True)
	note_meaning		= models.TextField(default='', blank=True, null=True)
	langguage_meaning	= models.CharField(max_length=80, blank=True, null=True)
	learned				= models.BooleanField(default=False)

	def __str__(self):
		return 'Vocabulary #%s' % self.pk

	class Meta:
		db_table 			= 'vocabularys'
		verbose_name_plural = 'Vocabularys'
		