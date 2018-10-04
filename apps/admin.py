from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.models import AppInfo
# Register your models here.

class AppInfoAdmin(admin.ModelAdmin):
	# ...
	search_fields = ['key']

	try:
		if AppInfo.objects.count()==0:
			AppInfo.objects.create(key='name', value="EnglishBigger")
			AppInfo.objects.create(key='version', value="")
			AppInfo.objects.create(key='description', value="")
			AppInfo.objects.create(key='developers', value="")
			AppInfo.objects.create(key='url_app', value="")
			AppInfo.objects.create(key='release_date', value='')
			print('Initialize the app information successfully!')
	except Exception as e:
		print(str(e))


admin.site.register(AppInfo, AppInfoAdmin)