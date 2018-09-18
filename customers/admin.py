from django.contrib import admin
from django.contrib.auth import get_user_model

from customers.models import Feedback
# Register your models here.

class FeedbackAdmin(admin.ModelAdmin):
	"""docstring for FeedbackAdmin"""
	list_display = ('__str__', 'email', 'date_post')
	list_filter = ['date_post']
	search_fields = ['email']

	def email(self, obj):
		return 	get_user_model().objects.filter(pk=obj.user_id).email

admin.site.register(Feedback, FeedbackAdmin)