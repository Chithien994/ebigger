from django.db.models.signals import post_save
from django.dispatch import receiver

from topics.models import Privileged

@receiver(post_save, sender=Privileged)
def create_privileged(sender, instance, created, **kwargs):
	if created:
		# instance.objects.created(key=1, name="Public")
		# instance.objects.created(key=2, name="Private")
		# instance.objects.created(key=3, name="Protected")
		Privileged.objects.create(privileged=instance)

@receiver(post_save, sender=Privileged)
def save_privileged(sender, instance, **kwargs):
	instance.Privileged.save()