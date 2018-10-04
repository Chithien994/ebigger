from django.contrib.auth import get_user_model
from rest_framework import permissions

from topics.models import Topic
from api import views

User = get_user_model()

#Permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
	"""
	Object-level permission to only allow owners of an object to edit it.
	Assumes the model instance has an `owner` attribute.
	"""
	def has_object_permission(self, request, view, obj):
	    # Read permissions are allowed to any request,
	    # Method GET 1 object, PUT, PATCH, DELETE
	    print('has object permission: ',request.method)
	    if request.method in ('PUT', 'PATCH', 'DELETE','GET'):
	    	return check(request, str(view), obj)
	    return False
	    

	def has_permission(self, request, view):
		# Method GET all, POST
		print('has permission: ',request.method)
		if request.method in ('POST','GET'):
			return check(request, str(view))
		return True
		



def check(request, view, obj=None):
	if request.method in permissions.SAFE_METHODS:
		return True

	if 'UserViewSet' in view:
		return userCheckPS(request, obj)
	elif 'TopicViewSet' in view:
		return topicCheckPS(request, obj)
	elif 'VocabularyViewSet' in view:
		return vobCheckPS(request, obj)
	return False

def isAdmin(myUserID):
	user = User.objects.get(pk=myUserID)
	if user:
		return user.is_admin
	return False

def userCheckPS(request, obj=None):
	myUserID = request.user.id
	if isAdmin(myUserID):
		return True
	if not obj:
		#Put or Patch
		return True
	elif myUserID == obj.id:
		return True
	return False

def topicCheckPS(request, obj=None):
	myUserID = request.user.id
	if isAdmin(myUserID):
		return True
	if obj and myUserID == obj.user_id:
		#Put or Patch
		return True
	elif request.data.get('user',''):
		#Post
		if myUserID==request.data.get('user',''):
			return True
	return False

def vobCheckPS(request, obj=None):
	myUserID = request.user.id
	if isAdmin(myUserID):
		return True
	topicID = ''
	if obj:
		topicID = obj.topic_id
	else:
		topicID = request.data.get('topic','')
	try:
		topic = Topic.objects.get(pk=topicID)
		user = User.objects.get(pk=topic.user_id)
		if user.id==myUserID:
			return True
	except Exception as e:
		return False
	return False