from io import BytesIO
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .models import Profile


class AuthenticationTests(TestCase):
    def setUp(self):
        self.registration = {
            "first_name": "Maria", "last_name": "Santos", "username": "maria",
            "email": "maria@example.com", "password1": "Cedar!Orbit72River",
            "password2": "Cedar!Orbit72River",
        }

    def create_user(self, **changes):
        details = {"username": "maria", "first_name": "Maria",
                   "password": self.registration["password1"]}
        details.update(changes)
        return User.objects.create_user(**details)

    def test_registration_saves_details_and_hashed_password(self):
        response = self.client.post(reverse("media_activity:register"), self.registration, follow=True)
        self.assertRedirects(response, reverse("media_activity:login"))
        self.assertContains(response, "Account created successfully")
        user = User.objects.get(username="maria")
        self.assertEqual((user.first_name, user.last_name, user.email),
                         ("Maria", "Santos", "maria@example.com"))
        self.assertNotEqual(user.password, self.registration["password1"])
        self.assertTrue(user.check_password(self.registration["password1"]))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_duplicate_username(self):
        self.create_user()
        response = self.client.post(reverse("media_activity:register"), self.registration)
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_password_mismatch(self):
        self.registration["password2"] = "Different!Password73"
        response = self.client.post(reverse("media_activity:register"), self.registration)
        self.assertIn("password2", response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_required_fields(self):
        response = self.client.post(reverse("media_activity:register"), {})
        self.assertEqual(set(response.context["form"].errors), set(self.registration))
        self.assertFalse(User.objects.exists())

    def test_invalid_email(self):
        self.registration["email"] = "not-an-email"
        response = self.client.post(reverse("media_activity:register"), self.registration)
        self.assertIn("email", response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_builtin_password_validators(self):
        for password in ["Q!2z", "123456789", "password", "maria"]:
            with self.subTest(password=password):
                self.registration.update(password1=password, password2=password)
                response = self.client.post(reverse("media_activity:register"), self.registration)
                self.assertIn("password2", response.context["form"].errors)
                self.assertFalse(User.objects.exists())

    def test_successful_login_and_personalized_profile(self):
        user = self.create_user()
        response = self.client.post(reverse("media_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
        }, follow=True)
        self.assertRedirects(response, reverse("media_activity:profile"))
        self.assertContains(response, "Maria")
        self.assertContains(response, "@maria")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_incorrect_credentials(self):
        self.create_user()
        for username in ["maria", "unknown"]:
            with self.subTest(username=username):
                response = self.client.post(reverse("media_activity:login"), {
                    "username": username, "password": "wrong",
                })
                self.assertTrue(response.context["form"].non_field_errors())
                self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_cannot_log_in(self):
        self.create_user(is_active=False)
        response = self.client.post(reverse("media_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
        })
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_anonymous_home_redirect(self):
        self.assertRedirects(self.client.get(reverse("media_activity:home")), reverse("media_activity:login"))

    def test_username_fallback(self):
        self.client.force_login(self.create_user(first_name=""))
        self.assertContains(self.client.get(reverse("media_activity:profile")), '<h1 id="profile-name">maria</h1>', html=True)

    def test_authenticated_users_skip_auth_forms(self):
        self.client.force_login(self.create_user())
        for page in ["media_activity:login", "media_activity:register"]:
            self.assertRedirects(self.client.get(reverse(page)), reverse("media_activity:profile"))

    def test_logout_removes_access_and_requires_post(self):
        self.client.force_login(self.create_user())
        self.assertEqual(self.client.get(reverse("media_activity:logout")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.post(reverse("media_activity:logout")), reverse("media_activity:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.get(reverse("media_activity:profile")), "/static-media/login/?next=/static-media/profile/")

    def test_all_post_forms_require_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        for page in ["media_activity:register", "media_activity:login", "media_activity:logout"]:
            self.assertEqual(browser.post(reverse(page), {}).status_code, 403)

    def test_complete_flow_with_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        browser.get(reverse("media_activity:register"))
        response = browser.post(reverse("media_activity:register"), self.registration,
                                HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 302)
        response = browser.post(reverse("media_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
        }, HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 302)
        self.assertContains(browser.get(reverse("media_activity:profile")), "@maria")
        response = browser.post(reverse("media_activity:logout"), {},
                                HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", browser.session)

    def test_login_does_not_follow_untrusted_next_url(self):
        self.create_user()
        response = self.client.post(reverse("media_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
            "next": "https://example.com",
        })
        self.assertRedirects(response, reverse("media_activity:profile"))

    def test_login_follows_safe_next_url(self):
        self.create_user()
        destination = reverse("media_activity:edit_profile_picture")
        response = self.client.post(reverse("media_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
            "next": destination,
        })
        self.assertRedirects(response, destination)


class ProfilePictureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="maria", password="Cedar!Orbit72River",
            first_name="Maria", last_name="Santos", email="maria@example.com",
        )
        self.other_user = User.objects.create_user(username="alex", password="Cedar!Orbit72River")
        self.media_settings = override_settings(STORAGES={
            "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
        })
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)

    def image_file(self, name="photo.png", image_format="PNG", size=(20, 20)):
        content = BytesIO()
        if size == (1600, 1200):
            image = Image.frombytes("RGB", size, os.urandom(1600 * 1200 * 3))
        else:
            image = Image.new("RGB", size, "blue")
        image.save(content, format=image_format)
        return SimpleUploadedFile(name, content.getvalue(), content_type="image/png")

    def test_profile_is_private_and_default_image_is_shown(self):
        profile_url = reverse("media_activity:profile")
        edit_url = reverse("media_activity:edit_profile_picture")
        self.assertRedirects(self.client.get(profile_url), f"/static-media/login/?next={profile_url}")
        self.assertRedirects(self.client.get(edit_url), f"/static-media/login/?next={edit_url}")
        self.client.force_login(self.user)
        response = self.client.get(profile_url)
        self.assertContains(response, "Maria Santos")
        self.assertContains(response, "maria@example.com")
        self.assertContains(response, "default-profile.svg")
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_upload_replace_and_keep_users_separate(self):
        self.client.force_login(self.user)
        edit_url = reverse("media_activity:edit_profile_picture")
        response = self.client.post(edit_url, {"profile_picture": self.image_file()})
        self.assertRedirects(response, reverse("media_activity:profile"))
        first_name = Profile.objects.get(user=self.user).profile_picture.name
        self.assertTrue(first_name.startswith("profile_pictures/"))
        self.assertContains(self.client.get(reverse("media_activity:profile")), first_name)

        self.client.post(edit_url, {"profile_picture": self.image_file("new.webp", "WEBP")})
        self.assertTrue(Profile.objects.get(user=self.user).profile_picture.name.endswith("new.webp"))
        self.assertFalse(Profile.objects.filter(user=self.other_user).exists())

        self.client.post(reverse("media_activity:logout"))
        self.client.login(username="maria", password="Cedar!Orbit72River")
        self.assertContains(self.client.get(reverse("media_activity:profile")), "new.webp")
        self.client.force_login(self.other_user)
        self.assertContains(self.client.get(reverse("media_activity:profile")), "default-profile.svg")

    def test_invalid_uploads_do_not_change_picture(self):
        self.client.force_login(self.user)
        edit_url = reverse("media_activity:edit_profile_picture")
        invalid_files = [
            {},
            {"profile_picture": SimpleUploadedFile("fake.png", b"not an image")},
            {"profile_picture": self.image_file("photo.gif")},
        ]
        for upload in invalid_files:
            with self.subTest(upload=upload):
                response = self.client.post(edit_url, upload)
                self.assertEqual(response.status_code, 200)
                self.assertIn("profile_picture", response.context["form"].errors)
                self.assertFalse(Profile.objects.get(user=self.user).profile_picture)

        large_response = self.client.post(edit_url, {
            "profile_picture": self.image_file("large.png", size=(1600, 1200)),
        })
        self.assertContains(large_response, "smaller than 5 MB")

    def test_upload_requires_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.user)
        self.assertEqual(browser.post(reverse("media_activity:edit_profile_picture"), {}).status_code, 403)
