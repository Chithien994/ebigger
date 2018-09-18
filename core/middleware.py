from django.http import Http404, HttpResponse

from django.contrib.contenttypes.models import ContentType
from django.db import connection, utils
from django.middleware.csrf import MiddlewareMixin


try:
    from django.conf import settings

    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
    XS_SHARING_ALLOWED_HEADERS = settings.XS_SHARING_ALLOWED_HEADERS
    XS_SHARING_ALLOWED_CREDENTIALS = settings.XS_SHARING_ALLOWED_CREDENTIALS
except AttributeError:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
    XS_SHARING_ALLOWED_HEADERS = 'Authorization, X-Requested-With, Content-Type, Access-Control-Allow-Origin'
    XS_SHARING_ALLOWED_CREDENTIALS = 'true'


class DisableCsrfMiddleware(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)