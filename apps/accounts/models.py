from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    phone = models.CharField(max_length=30, blank=True)
    must_change_password = models.BooleanField(default=False)

    @property
    def is_admin_role(self):
        return self.role == self.Roles.ADMIN or self.is_superuser

    @property
    def is_teacher_role(self):
        return self.role == self.Roles.TEACHER

    @property
    def is_student_role(self):
        return self.role == self.Roles.STUDENT


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(
        "core.Department",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_profiles",
    )
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
