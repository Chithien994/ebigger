from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Feedback(models.Model):
	"""docstring for Feedback"""
	user_id		= models.ForeignKey(get_user_model(), related_name='feedback', on_delete=models.CASCADE)
	content 	= models.TextField(default='', blank=True, null=True)
	date_post 	= models.DateTimeField('Created', auto_now_add=True, editable=False)
	new_post 	= models.BooleanField(default=True)
	
	def __str__(self):
		return 'Feedback #%s' % self.pk

	class Meta:
		db_table 			= 'feedbacks'
		verbose_name_plural = 'Feedbacks'