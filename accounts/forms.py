"""
accounts/forms.py - Registration and login forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """Extended registration form with email field."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
        }),
        help_text="Required. Enter a valid email address.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            # Set friendly placeholders
            placeholders = {
                "username": "Choose a username",
                "password1": "Create a strong password",
                "password2": "Repeat your password",
            }
            if field_name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[field_name]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Login form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Username",
            "autofocus": True,
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Password",
        })