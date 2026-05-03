from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "role", "phone")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


class StaffUserCreateForm(CustomUserCreationForm):
    class Meta(CustomUserCreationForm.Meta):
        fields = ("username", "email", "first_name", "last_name", "role", "phone")

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role not in {User.Roles.ADMIN, User.Roles.TEACHER, User.Roles.STUDENT}:
            raise forms.ValidationError("Choose a valid role.")
        return role
