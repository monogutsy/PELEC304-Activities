from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("login_activity:home")

    form = RegisterForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("login_activity:login")
    return render(request, "login_activity/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("login_activity:home")

    form = LoginForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("login_activity:home")
    return render(request, "login_activity/login.html", {"form": form})


@never_cache
@login_required(login_url="login_activity:login")
def home_view(request):
    return render(request, "login_activity/home.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login_activity:login")
