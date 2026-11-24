from django.urls import path

from . import views

app_name = "media_activity"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit-picture/", views.edit_profile_picture_view, name="edit_profile_picture"),
]
