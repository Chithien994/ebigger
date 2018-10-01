import requests
import json

def sendCode(phone_number):
    url         = 'https://api.authy.com/protected/json/phones/verification/start'
    data        = {"api_key":"kZgT2j8Q9f4p4Erv9hLKqcjo5lnOcgb6","via":"sms","phone_number":phone_number,"country_code":"84"}
    response    = requests.post(url, data=data)
    print('response: %s'%str(response.json))
    if '200' in str(response.json):
        return True
    return False

def checkCode(phone_number,code):
    url         = 'https://api.authy.com/protected/json/phones/verification/check'
    data        = {"api_key":"kZgT2j8Q9f4p4Erv9hLKqcjo5lnOcgb6","verification_code":code,"phone_number":phone_number,"country_code":"84"}
    response    = requests.get(url, data=data)
    response.headers['content-type']
    response.encoding

    print('response: %s'%str(response.json()))
    print('response: %s'%str(response.text))
    print('response: %s'%str(response.status_code))
    if 200 == response.status_code:
        return True
    return False