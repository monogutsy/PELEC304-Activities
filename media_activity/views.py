from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfilePictureForm, RegisterForm
from .models import Profile


def home_view(request):
    if request.user.is_authenticated:
        return redirect("media_activity:profile")
    return redirect("media_activity:login")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("media_activity:profile")

    form = RegisterForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("media_activity:login")
    return render(request, "media_activity/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("media_activity:profile")

    form = LoginForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        next_url = request.POST.get("next", "")
        if url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
            return redirect(next_url)
        return redirect("media_activity:profile")
    next_url = request.POST.get("next", "") or request.GET.get("next", "")
    return render(request, "media_activity/login.html", {"form": form, "next": next_url})


@never_cache
@login_required(login_url="media_activity:login")
def profile_view(request):
    # get_or_create also gives accounts made before this activity a profile.
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "media_activity/profile.html", {"profile": profile})


@login_required(login_url="media_activity:login")
def edit_profile_picture_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile picture was updated.")
            return redirect("media_activity:profile")
    else:
        form = ProfilePictureForm(instance=profile)
    return render(request, "media_activity/edit_profile_picture.html", {"form": form, "profile": profile})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("media_activity:login")
