from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("SCMS role", {"fields": ("role", "phone", "must_change_password")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("SCMS role", {"fields": ("role", "phone", "email", "first_name", "last_name")}),
    )
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "created_at")
    list_filter = ("department",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
