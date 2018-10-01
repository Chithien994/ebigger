from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from rest_framework.views import csrf_exempt
from django.contrib.auth import get_user_model
from sms.send_sms import twilioSMS


from django.template.loader import get_template

class IndexView(generic.ListView):
	template_name = 'sms/index.html'
	context_object_name = 'objects'

	def get_queryset(self):
	    return
@csrf_exempt
def send(request):
	phone_number = request.POST.get('phone_number','')
	message = request.POST.get('message','')
	context = {'code':400,'message':'Please enter the content!'}
	if message:
		context = {'code':200,'message':'Send a message successfully!'}
		cf, msg = twilioSMS(phone_number, message)
		if not cf:
			context = {'code':400,'message':msg}
	
	return render(request, 'sms/index.html', context)
