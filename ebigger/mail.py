import os

EMAIL_BACKEND 		= 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST 			= os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_NAME 	= os.environ.get('EMAIL_HOST_NAME', 'EnglishBigger')
EMAIL_HOST_USER 	= os.environ.get('EMAIL_HOST_USER', 'BigTest.TCN@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'MyBigTest@994')
DEFAULT_FROM_EMAIL 	= os.environ.get('DEFAULT_FROM_EMAIL','BigTest.TCN@gmail.com')
EMAIL_FROM 			= os.environ.get('EMAIL_FROM','BigTest.TCN@gmail.com')
EMAIL_PORT 			= os.environ.get('EMAIL_PORT', 465)
EMAIL_USE_SSL 		= True