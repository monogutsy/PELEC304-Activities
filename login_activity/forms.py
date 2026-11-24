from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(label="Email address", max_length=254)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "first_name": "Enter your first name",
            "last_name": "Enter your last name",
            "username": "Enter your username",
            "email": "Enter your email address",
            "password1": "Enter your password",
            "password2": "Re-enter your password",
        }
        autocomplete = {
            "first_name": "given-name",
            "last_name": "family-name",
            "username": "username",
            "email": "email",
            "password1": "new-password",
            "password2": "new-password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "placeholder": placeholders[name],
                "autocomplete": autocomplete[name],
            })
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = (
            "Use at least 8 characters and choose a password that is difficult to guess."
        )
        self.fields["password2"].label = "Confirm password"
        self.fields["password2"].help_text = ""


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Enter your username",
            "autocomplete": "username",
        })
        self.fields["username"].widget.attrs.pop("autofocus", None)
        self.fields["password"].widget.attrs.update({
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        })
