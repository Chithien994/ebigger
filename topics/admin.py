from django.contrib import admin
from topics.models import Topic, Vocabulary, Privileged

# Register your models here.
class TopicAdmin(admin.ModelAdmin):
    # ...
	list_display = ('__str__', 'name', 'number_vocabulary','last_action')
	list_filter = ['last_action']
	search_fields = ['name']

	def number_vocabulary(self, obj):
		return Vocabulary.objects.filter(topic=obj).count()

class VocabularyAdmin(admin.ModelAdmin):
	"""docstring for VocabularyAdmin"""
	list_display = ('__str__', 'note_source', 'note_meaning', 'learned')
	list_filter = ['last_action']
	search_fields = ['note_source', 'note_meaning']
		
class PrivilegedAdmin(admin.ModelAdmin):
	"""docstring for PrivilegedAdmin"""
	list_display = ('__str__', 'name')
	try:
		if Privileged.objects.count() == 0:
			Privileged.objects.create(key=1, name="Public")
			Privileged.objects.create(key=2, name="Private")
			Privileged.objects.create(key=3, name="Protected")
	except Exception as e:
		print(str(e))
		

admin.site.register(Topic, TopicAdmin)
admin.site.register(Vocabulary, VocabularyAdmin)
admin.site.register(Privileged, PrivilegedAdmin)
