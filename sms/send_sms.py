
from __future__ import print_function
import requests
import json
import sys
import os
from telesign.messaging import MessagingClient
from telesign.util import random_with_n_digits
from telesign.rest import RestClient
from django.conf import settings
from twilio.rest import Client, TwilioRestClient
from twilio.http.http_client import TwilioHttpClient

def nexmoSMS(phone_number, message):
    url         = 'https://api.nexmo.com/verify/json'
    data        = {"api_key":"fb8ada56","api_secret":"3JmzdT0FWmTgjQl3","number":"+84%s"%phone_number,"brand":message}
    response    = requests.post(url, data=data)
    response.headers['content-type']
    response.encoding
    print('response: %s'%str(response.json))
    if 200 == response.status_code:
        return True
    return False

def sendCode(phone_number, message):
    url         = 'https://api.authy.com/protected/json/phones/verification/start'
    data        = {"api_key":"kZgT2j8Q9f4p4Erv9hLKqcjo5lnOcgb6","via":"sms","phone_number":phone_number,"country_code":"84"}
    response    = requests.post(url, data=data)
    response.headers['content-type']
    response.encoding
    print('response: %s'%str(response.json))
    if 200 == response.status_code:
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
    response.headers['content-type']
    response.encoding
    print('response: %s'%str(response.json))
    if 209 == response.status_code:
        return True
    return False


def twilioSMS(phone_number, message):
    print(phone_number,message)
    er = '';
    if phone_number:
        if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM_NUMBER]):
            try:
                proxy_client = TwilioHttpClient()
                proxy_client.session.proxies = {'https://127.0.0.1:8000','http://127.0.0.1:8000','https://api.twilio.com:443','http://127.0.0.1:3128','https://127.0.0.1:3128'}
                twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN,http_client=proxy_client)
                twilio_client.messages.create(
                    body=str(message),
                    to=str('+84%s'%(phone_number)),
                    from_=settings.TWILIO_FROM_NUMBER
                )
                return True, er
            except Exception as e:
                er=e
                print(e)
        else:
            print('Twilio credentials are not set')
    return False, er