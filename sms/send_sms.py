
from __future__ import print_function
import requests
import json
import sys
from telesign.messaging import MessagingClient
from telesign.util import random_with_n_digits
from telesign.rest import RestClient
from django.conf import settings
from twilio.rest import Client, TwilioRestClient

def nexmoSMS(self):
    url         = 'https://api.nexmo.com/verify/json'
    data        = '{"api_key":"fb8ada56","api_secret":"3JmzdT0FWmTgjQl3","number":"+84866505510","brand":"EnglishBigger VerifyTest"}'
    headers     = {"Content-Type" : "application/json", "api-key" : "fb8ada56"}
    response    = requests.post(url, data=json.dumps(data),headers=headers)
    print('response: %s'%str(response.json))
    if '200' in str(response.json):
        return True
    return False

def telesignSMS(self):
    if sys.version[0]=="3": raw_input=input
    customer_id     = "8E97966D-878D-42A5-A863-12004F58C35F"
    api_key         = "Q8dFhf23Js9XcxYSwfALvylu9fWA5C6KpVE4PvPhW61yW+WngguxhfphvsyRS9efo1ofGfXzuiruUq9ExwLE8g=="

    phone_number    = "84866505510"
    message         = "Your EnglishBigger verification code is %s"%(self.pin)
    message_type    = "OTP"

    response        = MessagingClient(customer_id, api_key).message(phone_number, message, message_type)
    print('response: %s'%str(response.json))
    if '290' in str(response.json):
        return True
    return False


def twilioSMS(phone_number, message):
    print(phone_number,message)
    er = '';
    if phone_number:
        if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM_NUMBER]):
            try:
                twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                twilio_client.messages.create(
                    body=str(message),
                    to=str('+84%s'%(phone_number)),
                    from_=settings.TWILIO_FROM_NUMBER
                )
                return True, e
            except Exception as e:
                er=e
                print(e)
        else:
            print('Twilio credentials are not set')
    return False, e