from django.db import models

# Create your models here.

class AppInfo(models.Model):
	key 	= models.CharField(max_length=100, unique=True)
	value 	= models.TextField(default='', blank=True, null=True)
	def __str__(self):
		return '%s#%s' % (self.pk, self.key)

	class Meta:
		db_table 			= 'appinfo'
		verbose_name_plural = 'AppInfo'