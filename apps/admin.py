from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.models import AppInfo
# Register your models here.

class AppInfoAdmin(admin.ModelAdmin):
	# ...
	list_display = ('__str__', 'version', 'developers', 'user_number')
	list_filter = ['release_date']
	search_fields = ['name']

	def user_number(self, obj):
		return get_user_model().objects.count()

admin.site.register(AppInfo, AppInfoAdmin)