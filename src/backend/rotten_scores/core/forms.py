from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from . import models
from mongoengine import DoesNotExist


class UsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'login-input',
            'autocomplete': 'username',
            'id': 'id_username'
        }),
        label=_("Username"),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'login-input',
            'autocomplete': 'current-password',
            'id': 'id_password'
        }),
        label=_("Password"),
        strip=False,
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = models.User.objects.get(username=username)
        except DoesNotExist:
            raise forms.ValidationError("Invalid username or password")
        return user
