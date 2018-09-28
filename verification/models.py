from django.contrib.auth import get_user_model
from django.db import models
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from django_extensions.db.models import TimeStampedModel
from django.db import models
from random import randint
from verification.send_sms import nexmoSMS, telesignSMS, twilioSMS
from core.utils import get_site_url, send_email, iHttpResponse


class PhoneManager(TimeStampedModel):
	user        = models.ForeignKey(get_user_model(), related_name='phonemanager', on_delete=models.CASCADE)
	verified    = models.BooleanField(default=False)
	pin         = models.CharField(max_length=6, default=str(randint(100000, 999999)))
	sent        = models.BooleanField(default=False)
	country_code= models.CharField(max_length=4)
	phone_number= models.CharField(max_length=20)

	def __str__(self):
		return 'Phone: (+%s) %s' % (self.country_code, self.phone_number)

	class Meta:
		db_table = 'phone_manager'
		verbose_name_plural = 'Phone Manager'

	def send_verification(self):
		if twilioSMS(self):
			return True
		return False

class EmailManager(models.Model):
	user        = models.ForeignKey(get_user_model(), related_name='emailmanager', on_delete=models.CASCADE)
	verified    = models.BooleanField(default=False)
	email 		= models.EmailField(max_length=80)

	def __str__(self):
		return 'Email: %s' % self.user

	class Meta:
		db_table = 'email_manager'
		verbose_name_plural = 'Email Manager'

	def send_verification(self):
		SITE_URL = get_site_url()
		code, message = None, None
		if self.user:
		    subject         = "Verify Email"
		    message_html    = "email/verify_email.html"
		    email_from      = ""
		    email_to        = [self.user.email]

		    token           = default_token_generator.make_token(self.user)
		    uidb64          = urlsafe_base64_encode(force_bytes(self.user.pk))
		    obj_model = {
		        'phone_number': self.user.phone_number,
		        'first_name': self.user.first_name,
		        'verify_email_url': SITE_URL + reverse('verifyemail',
		                                             kwargs={'uidb64': str(uidb64, 'utf-8'), 'token': token})
		    }
		    print('verify_email_url', obj_model['verify_email_url'])
		    send_email(subject, message_html, email_from, email_to, obj_model)
		    return True
		return False

