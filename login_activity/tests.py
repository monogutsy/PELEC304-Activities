from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


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
        response = self.client.post(reverse("login_activity:register"), self.registration, follow=True)
        self.assertRedirects(response, reverse("login_activity:login"))
        self.assertContains(response, "Account created successfully")
        user = User.objects.get(username="maria")
        self.assertEqual((user.first_name, user.last_name, user.email),
                         ("Maria", "Santos", "maria@example.com"))
        self.assertNotEqual(user.password, self.registration["password1"])
        self.assertTrue(user.check_password(self.registration["password1"]))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_duplicate_username(self):
        self.create_user()
        response = self.client.post(reverse("login_activity:register"), self.registration)
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_password_mismatch(self):
        self.registration["password2"] = "Different!Password73"
        response = self.client.post(reverse("login_activity:register"), self.registration)
        self.assertIn("password2", response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_required_fields(self):
        response = self.client.post(reverse("login_activity:register"), {})
        self.assertEqual(set(response.context["form"].errors), set(self.registration))
        self.assertFalse(User.objects.exists())

    def test_invalid_email(self):
        self.registration["email"] = "not-an-email"
        response = self.client.post(reverse("login_activity:register"), self.registration)
        self.assertIn("email", response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_builtin_password_validators(self):
        for password in ["Q!2z", "123456789", "password", "maria"]:
            with self.subTest(password=password):
                self.registration.update(password1=password, password2=password)
                response = self.client.post(reverse("login_activity:register"), self.registration)
                self.assertIn("password2", response.context["form"].errors)
                self.assertFalse(User.objects.exists())

    def test_successful_login_and_personalized_home(self):
        user = self.create_user()
        response = self.client.post(reverse("login_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
        }, follow=True)
        self.assertRedirects(response, reverse("login_activity:home"))
        self.assertContains(response, "Welcome, Maria!")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_incorrect_credentials(self):
        self.create_user()
        for username in ["maria", "unknown"]:
            with self.subTest(username=username):
                response = self.client.post(reverse("login_activity:login"), {
                    "username": username, "password": "wrong",
                })
                self.assertTrue(response.context["form"].non_field_errors())
                self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_cannot_log_in(self):
        self.create_user(is_active=False)
        response = self.client.post(reverse("login_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
        })
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_anonymous_home_redirect(self):
        self.assertRedirects(self.client.get(reverse("login_activity:home")), "/login-register/login/?next=/login-register/")

    def test_username_fallback(self):
        self.client.force_login(self.create_user(first_name=""))
        self.assertContains(self.client.get(reverse("login_activity:home")), "Welcome, maria!")

    def test_authenticated_users_skip_auth_forms(self):
        self.client.force_login(self.create_user())
        for page in ["login_activity:login", "login_activity:register"]:
            self.assertRedirects(self.client.get(reverse(page)), reverse("login_activity:home"))

    def test_logout_removes_access_and_requires_post(self):
        self.client.force_login(self.create_user())
        self.assertEqual(self.client.get(reverse("login_activity:logout")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.post(reverse("login_activity:logout")), reverse("login_activity:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.get(reverse("login_activity:home")), "/login-register/login/?next=/login-register/")

    def test_all_post_forms_require_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        for page in ["login_activity:register", "login_activity:login", "login_activity:logout"]:
            self.assertEqual(browser.post(reverse(page), {}).status_code, 403)

    def test_complete_flow_with_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        browser.get(reverse("login_activity:register"))
        response = browser.post(reverse("login_activity:register"), self.registration,
                                HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 302)
        response = browser.post(reverse("login_activity:login"), {
            "username": "maria", "password": self.registration["password1"],
        }, HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 302)
        self.assertContains(browser.get(reverse("login_activity:home")), "Welcome, Maria!")
        response = browser.post(reverse("login_activity:logout"), {},
                                HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", browser.session)

    def test_login_does_not_follow_untrusted_next_url(self):
        self.create_user()
        response = self.client.post(reverse("login_activity:login") + "?next=https://example.com", {
            "username": "maria", "password": self.registration["password1"],
        })
        self.assertRedirects(response, reverse("login_activity:home"))
