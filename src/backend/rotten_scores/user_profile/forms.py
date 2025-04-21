from django import forms
from django.core.validators import MinLengthValidator
from pymongo import MongoClient
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime
from django.contrib.auth.hashers import make_password
from core.models import User


class ChangePersonalDataForm(forms.Form):
    username = forms.CharField(
        label="Username",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "login-input"
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            "class": "login-input"
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username is None or username.strip() == '':
            cleaned_data['username'] = self.user.username

        if email is None or email.strip() == '':
            cleaned_data['email'] = self.user.email

        if not username and not email:
            raise forms.ValidationError("Please fill in at least one of the fields: Username or Email.")

        if username and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            self.add_error('username', "This username is already taken.")

        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            self.add_error('email', "This email is already used.")

        return cleaned_data

    def save(self):
        username = self.cleaned_data.get('username', self.user.username)
        email = self.cleaned_data.get('email', self.user.email)

        try:
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]

            result = db.users.update_one(
                {'_id': self.user.id},
                {'$set': {'username': username, 'email': email, 'lastModified': datetime.now()}}
            )

            if result.matched_count == 0:
                raise ValidationError("User update failed.")

            return self.user
        except Exception as e:
            raise ValidationError(f"Error updating user: {str(e)}")


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "login-input"}),
        validators=[MinLengthValidator(4)],
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "login-input"}),
        help_text="Must be at least 6 characters with 1 number and special character",
        validators=[MinLengthValidator(4)],
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "login-input"}),
        help_text="Must be at least 6 characters with 1 number and special character",
        validators=[MinLengthValidator(4)],
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('new_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if new_password and current_password and new_password == current_password:
            self.add_error('new_password', "New password cannot be the same as the current one.")

        return cleaned_data

    def save(self):
        new_password = self.cleaned_data['new_password']

        try:
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]

            result = db.users.update_one(
                {'_id': self.user.id},
                {'$set': {'hashedPassword': make_password(new_password), 'lastModified': datetime.now()}}
            )
            print(result)

            if result.matched_count == 0:
                raise ValidationError("Password update failed.")

            return self.user
        except Exception as e:
            raise ValidationError(f"Error updating password: {str(e)}")

