from django.db import models

# Create your models here.

class AppInfo(models.Model):
	name 		= models.CharField(max_length=50, unique=True)
	version 	= models.CharField(max_length=10, blank=True, null=True)
	description = models.TextField(default='', blank=True, null=True)
	developers 	= models.CharField(max_length=50, blank=True, null=True)
	url_app 	= models.CharField(max_length=250, blank=True, null=True)
	release_date= models.DateTimeField('Release date', editable=True, blank=True, null=True)
	def __str__(self):
		return '%s-%s' % (self.pk, self.name)

	class Meta:
		db_table 			= 'appinfo'
		verbose_name_plural = 'AppInfo'