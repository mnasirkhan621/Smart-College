from django.contrib import admin

from .models import BackupLog, FeeCategory, FeeStructure, Invoice, Payment


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("category", "course", "semester", "academic_year", "amount", "is_active")
    list_filter = ("category", "course", "academic_year", "semester", "is_active")
    search_fields = ("category__name", "course__name")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "student", "fee_structure", "total_amount", "paid_amount", "status", "due_date")
    list_filter = ("status", "fee_structure__category", "fee_structure__academic_year")
    search_fields = ("invoice_no", "student__registration_no", "student__full_name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "invoice", "amount", "payment_date", "method", "received_by")
    list_filter = ("method", "payment_date")
    search_fields = ("receipt_no", "invoice__invoice_no", "invoice__student__full_name")


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ("file_path", "status", "created_by", "created_at")
    list_filter = ("status",)
    search_fields = ("file_path", "notes")
