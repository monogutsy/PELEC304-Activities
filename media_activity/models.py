from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    # Each account owns one profile; the image file itself lives in MEDIA_ROOT.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True)

    def __str__(self):
        return self.user.username
