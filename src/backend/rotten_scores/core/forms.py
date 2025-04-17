from django import forms
from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "placeholder": "Username",
            "class": "login-input"
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
            "class": "login-input"
        }),
        strip=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            # Используем filter вместо get, чтобы избежать исключения
            user = User.objects.filter(username=username).first()

            if not user:
                raise forms.ValidationError("Invalid username or password")

            # Проверка пароля
            if not user.check_password(password):
                raise forms.ValidationError("Invalid username or password")

            # Сохраняем пользователя на форму для дальнейшего использования
            self.user = user

        return cleaned_data
