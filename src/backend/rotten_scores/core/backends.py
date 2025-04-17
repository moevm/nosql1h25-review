from bson import ObjectId
from django.contrib.auth.backends import BaseBackend
from . import models
from mongoengine.errors import DoesNotExist


class MongoEngineBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = models.User.objects.get(username=username)
            if user.hashedPassword == password:
                return user
        except DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            obj_id = ObjectId(user_id)
            return models.User.objects.get(id=obj_id)
        except (DoesNotExist, Exception):
            return None
