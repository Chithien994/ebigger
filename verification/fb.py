import requests

url = 'https://www.facebook.com/login.php?login_attempt=1' #the form's action url
par = {"email": "chithien994", "password": "Khong@994"} # the forms parameters
r = requests.post(url, data=par)
print (r.content) # you can't use r.text because of encoding