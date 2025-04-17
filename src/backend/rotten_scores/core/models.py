import mongoengine as me
from django.utils import timezone


class User(me.Document):
    username = me.StringField(max_length=150, unique=True, required=True)
    email = me.EmailField(unique=True)
    hashedPassword = me.StringField(required=True)
    role = me.StringField(choices=["user", "admin"], default="user")
    created_at = me.DateTimeField(default=timezone.now)
    last_modified = me.DateTimeField(default=timezone.now)

    meta = {
        'indexes': [
            'username',
            'email',
        ]
    }

    def __str__(self):
        return self.username
