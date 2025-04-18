from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models, DatabaseError
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from djongo.models import ObjectIdField


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.CharField(primary_key=True, editable=False, db_column='_id', max_length=24)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    hashedPassword = models.CharField(max_length=255)  # Храним хешированный пароль
    role = models.CharField(choices=[("user", "User"), ("admin", "Admin")], default="user", max_length=20)
    createdAt = models.DateTimeField(default=timezone.now)
    lastModified = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def check_password(self, raw_password):
        # Проверка пароля
        return check_password(raw_password, self.hashedPassword)

    def set_password(self, raw_password):
        self.hashedPassword = make_password(raw_password)  # Хеширование пароля

    def __str__(self):
        return self.username

    def is_staff(self):
        return self.is_admin

    @property
    def is_authenticated(self):
        return True

    def save(self, *args, **kwargs):
        try:
            return super().save(*args, **kwargs)
        except DatabaseError as e:
            if "did not affect any rows" in str(e):
                # Игнорируем ошибку, так как Djongo может не возвращать affected rows
                pass
            else:
                raise

    class Meta:
        db_table = 'users'
