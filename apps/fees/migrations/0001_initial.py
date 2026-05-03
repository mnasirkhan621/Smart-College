import decimal
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("academics", "0001_initial"),
        ("accounts", "0001_initial"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeeCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="BackupLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file_path", models.CharField(max_length=260)),
                ("status", models.CharField(default="CREATED", max_length=40)),
                ("notes", models.TextField(blank=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="backup_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="FeeStructure",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("due_days", models.PositiveSmallIntegerField(default=30)),
                ("is_active", models.BooleanField(default=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fee_structures", to="core.academicyear")),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="structures", to="fees.feecategory")),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fee_structures", to="academics.course")),
                ("semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fee_structures", to="core.semester")),
            ],
            options={
                "ordering": ("course", "semester", "category"),
                "unique_together": {("category", "course", "semester", "academic_year")},
            },
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice_no", models.CharField(max_length=40, unique=True)),
                ("issue_date", models.DateField(default=django.utils.timezone.localdate)),
                ("due_date", models.DateField()),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("paid_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10)),
                ("status", models.CharField(choices=[("UNPAID", "Unpaid"), ("PARTIAL", "Partial"), ("PAID", "Paid"), ("CANCELLED", "Cancelled")], default="UNPAID", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("fee_structure", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="fees.feestructure")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to="academics.studentprofile")),
            ],
            options={"ordering": ("-issue_date", "student__registration_no")},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("receipt_no", models.CharField(max_length=40, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_date", models.DateField(default=django.utils.timezone.localdate)),
                ("method", models.CharField(choices=[("CASH", "Cash"), ("BANK", "Bank"), ("ONLINE", "Online")], default="CASH", max_length=20)),
                ("reference_no", models.CharField(blank=True, max_length=80)),
                ("remarks", models.CharField(blank=True, max_length=180)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="fees.invoice")),
                ("received_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="received_payments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-payment_date", "-created_at")},
        ),
    ]
