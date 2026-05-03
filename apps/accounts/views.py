from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import StaffUserCreateForm
from .models import User


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_role


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ("role", "username")


class UserCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = StaffUserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    success_message = "User created successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.role == User.Roles.ADMIN:
            self.object.is_staff = True
            self.object.save(update_fields=["is_staff"])
        return response
