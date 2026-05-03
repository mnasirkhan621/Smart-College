import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("academics", "0001_initial"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("body", models.TextField()),
                ("audience", models.CharField(choices=[("ALL", "All Users"), ("ADMINS", "Admins"), ("TEACHERS", "Teachers"), ("STUDENTS", "Students")], default="ALL", max_length=20)),
                ("publish_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_notices", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-publish_at", "-created_at")},
        ),
        migrations.CreateModel(
            name="AttendanceSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("topic", models.CharField(blank=True, max_length=180)),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("SUBMITTED", "Submitted")], default="DRAFT", max_length=20)),
                ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_sessions", to="academics.teachersubjectassignment")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_attendance_sessions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-date", "-created_at"),
                "unique_together": {("assignment", "date")},
            },
        ),
        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("PRESENT", "Present"), ("ABSENT", "Absent"), ("LATE", "Late"), ("LEAVE", "Leave")], default="PRESENT", max_length=20)),
                ("remarks", models.CharField(blank=True, max_length=180)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="records", to="attendance.attendancesession")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="academics.studentprofile")),
            ],
            options={
                "ordering": ("student__registration_no",),
                "unique_together": {("session", "student")},
            },
        ),
    ]
