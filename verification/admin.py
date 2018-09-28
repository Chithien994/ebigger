from django.contrib import admin
from verification.models import EmailManager, PhoneManager
# Register your models here.
class EmailAdmin(admin.ModelAdmin):
	"""docstring for EmailAdmin"""
	list_display = ('email', 'username', 'verified')
	list_filter = ['verified']
	search_fields = ['email']

	def username(self, obj):
		return obj.user.email

class PhoneAdmin(admin.ModelAdmin):
	"""docstring for EmailAdmin"""
	list_display = ('__str__', 'username', 'sent' ,'verified')
	list_filter = ['verified']
	search_fields = ['phone_number']

	def username(self, obj):
		return obj.user.email


admin.site.register(PhoneManager,PhoneAdmin)
admin.site.register(EmailManager,EmailAdmin)