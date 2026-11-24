from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from media_activity.models import Profile


class CombinedProjectTests(TestCase):
    def test_anonymous_visitor_gets_404_at_homepage(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 404)

    def test_regular_user_gets_404_at_homepage(self):
        self.client.force_login(User.objects.create_user(username="regular"))
        self.assertEqual(self.client.get(reverse("home")).status_code, 404)

    def test_admin_login_allows_superuser_to_open_homepage(self):
        User.objects.create_superuser(username="staff", password="TestOnly!Pass123")
        response = self.client.post(reverse("admin:login") + "?next=/", {
            "username": "staff",
            "password": "TestOnly!Pass123",
            "next": "/",
        })
        self.assertRedirects(response, reverse("home"))

        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")
        self.assertIn("no-store", response.headers["Cache-Control"])
        for name in ["login_activity:home", "media_activity:home",
                     "students:student_list", "products:product-list"]:
            url = reverse(name)
            self.assertContains(response, f'href="{url}"')
            self.assertEqual(self.client.get(url, follow=True).status_code, 200)

    def test_templates_and_styles_do_not_collide(self):
        for app in ["login_activity", "media_activity"]:
            response = self.client.get(reverse(f"{app}:login"))
            self.assertTemplateUsed(response, f"{app}/login.html")
            self.assertTemplateUsed(response, f"{app}/base.html")
            self.assertContains(response, f"/static/{app}/css/style.css")
        self.assertIsNone(finders.find("css/style.css"))
        for asset in ["portal/home.css", "login_activity/css/style.css",
                      "media_activity/css/style.css", "students/css/style.css",
                      "media_activity/images/cover.svg", "media_activity/images/camera.svg",
                      "media_activity/images/default-profile.svg"]:
            self.assertIsNotNone(finders.find(asset), asset)

    def test_one_account_and_session_work_across_both_activities(self):
        user = User.objects.create_user(username="shared", password="TestOnly!Pass123")
        self.client.post(reverse("login_activity:login"), {
            "username": "shared", "password": "TestOnly!Pass123",
        })
        self.assertContains(self.client.get(reverse("login_activity:home")), "Welcome, shared!")
        self.assertContains(self.client.get(reverse("media_activity:profile")), "@shared")
        self.assertEqual(Profile.objects.get(user=user).user_id, user.pk)
        self.client.post(reverse("media_activity:logout"))
        for name in ["login_activity:home", "media_activity:profile"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)

    def test_duplicate_usernames_are_shared_between_registration_forms(self):
        User.objects.create_user(username="shared")
        for app in ["login_activity", "media_activity"]:
            response = self.client.post(reverse(f"{app}:register"), {
                "username": "shared", "first_name": "Test", "last_name": "Student",
                "email": "student@example.com", "password1": "TestOnly!Pass123",
                "password2": "TestOnly!Pass123",
            })
            self.assertIn("username", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_admin_login_and_all_app_models(self):
        self.assertRedirects(self.client.get("/admin/"), "/admin/login/?next=/admin/")
        self.client.force_login(User.objects.create_superuser(username="staff"))
        response = self.client.get("/admin/")
        self.assertContains(response, reverse("admin:students_student_changelist"))
        self.assertContains(response, reverse("admin:products_product_changelist"))
