import logging

from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ObjectDoesNotExist

from src.backend.core import models

from bson import ObjectId

logger = logging.getLogger(__name__)


class MongoEngineBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = models.User.objects.get(username=username)
            logger.info(f"Найден пользователь: {user.username}")
            if user.check_password(password):
                logger.info(f"Аутентификация прошла успешно для {username}")
                return user
        except ObjectDoesNotExist:
            logger.warning(f"Пользователь с именем {username} не найден")
        except Exception as e:
            logger.error(f"Ошибка при аутентификации: {e}")
        return None

    def get_user(self, user_id):
        try:
            for user in models.User.objects.all():
                if user.id == ObjectId(user_id):
                    return user
        except ObjectDoesNotExist:
            logger.warning(f"Пользователь с id {user_id} не найден")
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя по id {user_id}: {e}")
        return None