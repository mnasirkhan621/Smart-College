from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("academics/", include("apps.academics.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("exams/", include("apps.exams.urls")),
    path("fees/", include("apps.fees.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
