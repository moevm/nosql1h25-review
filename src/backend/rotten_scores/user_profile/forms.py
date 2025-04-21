from django import forms
import re
from core.models import User


class ChangePersonalDataForm(forms.Form):
    username = forms.CharField(
        label="Username",
        required=False,  # Теперь поле не обязательное
        widget=forms.TextInput(attrs={
            "class": "login-input"
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,  # Теперь поле не обязательное
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

        # Проверяем, чтобы хотя бы одно из полей было заполнено
        if not username and not email:
            raise forms.ValidationError("Please fill in at least one of the fields: Username or Email.")

        # Если заполнили username, проверяем его уникальность
        if username and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            self.add_error('username', "This username is already taken.")

        # Если заполнили email, проверяем его уникальность
        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            self.add_error('email', "This email is already used.")

        return cleaned_data

    def save(self):
        self.user.username = self.cleaned_data.get('username', self.user.username)
        self.user.email = self.cleaned_data.get('email', self.user.email)
        self.user.save()
        return self.user


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "login-input"}),
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "login-input"}),
        help_text="Must be at least 6 characters with 1 number and special character",
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "login-input"}),
        help_text="Must be at least 6 characters with 1 number and special character",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Incorrect current password.")
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        if not re.search(r'\d', new_password):
            raise forms.ValidationError("Password must contain at least one number.")
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if new_password and current_password and new_password == current_password:
            self.add_error('new_password', "New password cannot be the same as the current one.")

        return cleaned_data

    def save(self):
        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        self.user.save()

