from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.academics.models import Course, StudentProfile
from apps.core.models import AcademicYear, Semester, TimestampedModel


class FeeCategory(TimestampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class FeeStructure(TimestampedModel):
    category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name="structures")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="fee_structures")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="fee_structures")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="fee_structures")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_days = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("course", "semester", "category")
        unique_together = ("category", "course", "semester", "academic_year")

    def __str__(self):
        return f"{self.course.code} {self.semester.name} - {self.category.name}"


class Invoice(TimestampedModel):
    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIAL = "PARTIAL", "Partial"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="invoices")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name="invoices")
    invoice_no = models.CharField(max_length=40, unique=True)
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-issue_date", "student__registration_no")

    def __str__(self):
        return f"{self.invoice_no} - {self.student.full_name}"

    @property
    def balance(self):
        balance = self.total_amount - self.paid_amount
        return balance if balance > 0 else Decimal("0.00")

    def refresh_status(self):
        if self.status == self.Status.CANCELLED:
            return
        if self.paid_amount <= 0:
            self.status = self.Status.UNPAID
        elif self.paid_amount < self.total_amount:
            self.status = self.Status.PARTIAL
        else:
            self.status = self.Status.PAID


class Payment(TimestampedModel):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK = "BANK", "Bank"
        ONLINE = "ONLINE", "Online"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    receipt_no = models.CharField(max_length=40, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    reference_no = models.CharField(max_length=80, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="received_payments",
    )
    remarks = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ("-payment_date", "-created_at")

    def __str__(self):
        return f"{self.receipt_no} - {self.amount}"


class BackupLog(TimestampedModel):
    file_path = models.CharField(max_length=260)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="backup_logs",
    )
    status = models.CharField(max_length=40, default="CREATED")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.file_path
