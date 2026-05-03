from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from apps.academics.models import StudentProfile
from apps.accounts.views import AdminRequiredMixin

from .forms import FeeCategoryForm, FeeStructureForm, InvoiceForm, PaymentForm
from .models import BackupLog, FeeCategory, FeeStructure, Invoice, Payment


class FeeHomeView(AdminRequiredMixin, TemplateView):
    template_name = "fees/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoice_count"] = Invoice.objects.count()
        context["pending_count"] = Invoice.objects.exclude(status__in=[Invoice.Status.PAID, Invoice.Status.CANCELLED]).count()
        context["payment_count"] = Payment.objects.count()
        context["backup_logs"] = BackupLog.objects.all()[:5]
        return context


class FeeCategoryListView(AdminRequiredMixin, ListView):
    model = FeeCategory
    template_name = "fees/category_list.html"
    context_object_name = "categories"


class FeeCategoryCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    template_name = "fees/form.html"
    success_url = reverse_lazy("fees:category_list")
    success_message = "Fee category saved."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Fee Category"
        context["cancel_url"] = reverse("fees:category_list")
        return context


class FeeStructureListView(AdminRequiredMixin, ListView):
    model = FeeStructure
    template_name = "fees/structure_list.html"
    context_object_name = "structures"

    def get_queryset(self):
        return FeeStructure.objects.select_related("category", "course", "semester", "academic_year")


class FeeStructureCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = "fees/form.html"
    success_url = reverse_lazy("fees:structure_list")
    success_message = "Fee structure saved."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Fee Structure"
        context["cancel_url"] = reverse("fees:structure_list")
        return context


class InvoiceListView(AdminRequiredMixin, ListView):
    model = Invoice
    template_name = "fees/invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        return Invoice.objects.select_related("student", "fee_structure__category")


class InvoiceCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "fees/form.html"
    success_url = reverse_lazy("fees:invoice_list")
    success_message = "Invoice created."

    def form_valid(self, form):
        form.instance.refresh_status()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Invoice"
        context["cancel_url"] = reverse("fees:invoice_list")
        return context


class PaymentCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "fees/form.html"
    success_message = "Payment recorded."

    def form_valid(self, form):
        form.instance.received_by = self.request.user
        response = super().form_valid(form)
        invoice = self.object.invoice
        invoice.paid_amount += self.object.amount
        invoice.refresh_status()
        invoice.save(update_fields=["paid_amount", "status", "updated_at"])
        return response

    def get_success_url(self):
        return reverse("fees:receipt_detail", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Record Payment"
        context["cancel_url"] = reverse("fees:invoice_list")
        return context


class ReceiptAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        payment = self.get_object()
        if self.request.user.is_admin_role:
            return True
        student_profile = StudentProfile.objects.filter(user=self.request.user).first()
        return student_profile and payment.invoice.student_id == student_profile.id


class ReceiptDetailView(ReceiptAccessMixin, DetailView):
    model = Payment
    template_name = "fees/receipt_detail.html"
    context_object_name = "payment"


class PendingDuesView(AdminRequiredMixin, TemplateView):
    template_name = "fees/pending_dues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoices"] = Invoice.objects.exclude(
            status__in=[Invoice.Status.PAID, Invoice.Status.CANCELLED],
        ).select_related("student", "fee_structure__category")
        return context


class StudentFeeView(LoginRequiredMixin, TemplateView):
    template_name = "fees/student_fees.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = StudentProfile.objects.filter(user=self.request.user).first()
        context["student_profile"] = student_profile
        if not student_profile:
            context["invoices"] = []
            context["payments"] = []
            return context
        context["invoices"] = Invoice.objects.filter(student=student_profile).select_related("fee_structure__category")
        context["payments"] = Payment.objects.filter(invoice__student=student_profile).select_related("invoice")
        return context
