from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("login-register/", include("login_activity.urls")),
    path("static-media/", include("media_activity.urls")),
    path("students/", include("students.urls")),
    path("api/", include("products.urls")),
    path("admin/", admin.site.urls),
]

# PythonAnywhere serves uploaded files directly through its Web tab mapping.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
