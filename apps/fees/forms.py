from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import FeeCategory, FeeStructure, Invoice, Payment


class BaseFeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class FeeCategoryForm(BaseFeeForm):
    class Meta:
        model = FeeCategory
        fields = ("name", "description", "is_active")


class FeeStructureForm(BaseFeeForm):
    class Meta:
        model = FeeStructure
        fields = ("category", "course", "semester", "academic_year", "amount", "due_days", "is_active")


class InvoiceForm(BaseFeeForm):
    class Meta:
        model = Invoice
        fields = ("student", "fee_structure", "invoice_no", "issue_date", "due_date", "total_amount", "notes")
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        fee_structure = cleaned.get("fee_structure")
        if fee_structure:
            cleaned.setdefault("total_amount", fee_structure.amount)
        return cleaned


class PaymentForm(BaseFeeForm):
    class Meta:
        model = Payment
        fields = ("invoice", "receipt_no", "amount", "payment_date", "method", "reference_no", "remarks")
        widgets = {"payment_date": forms.DateInput(attrs={"type": "date"})}

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        invoice = self.cleaned_data.get("invoice")
        if invoice and amount > invoice.balance:
            raise forms.ValidationError("Payment cannot be greater than the invoice balance.")
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount


def next_due_date(days):
    return timezone.localdate() + timedelta(days=days)
