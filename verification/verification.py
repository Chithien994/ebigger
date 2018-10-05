import requests
import json
from core.models import Setting

def get_api_key():
    api_key = "kZgT2j8Q9f4p4Erv9hLKqcjo5lnOcgb6"
    for setting in Setting.objects.all():
        if 'sms_api_key' in setting.key:
            api_key = setting.value
            break
    return api_key

def sendCode(country_code, phone_number):
    url         = 'https://api.authy.com/protected/json/phones/verification/start'
    data        = {"api_key":get_api_key(),"via":"sms","phone_number":phone_number,"country_code":country_code}
    response    = requests.post(url, data=data)
    response.headers['content-type']
    response.encoding
    print('response: %s'%str(response.json))
    if 200 == response.status_code:
        return True
    return False

def checkCode(country_code, phone_number,code):
    url         = 'https://api.authy.com/protected/json/phones/verification/check'
    data        = {"api_key":get_api_key(),"verification_code":code,"phone_number":phone_number,"country_code":country_code}
    response    = requests.get(url, data=data)
    response.headers['content-type']
    response.encoding
    print('response: %s'%str(response.json()))
    if 200 == response.status_code:
        return True
    return False