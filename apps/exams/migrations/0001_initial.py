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
            name="GradeScale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=40, unique=True)),
                ("min_percentage", models.DecimalField(decimal_places=2, max_digits=5)),
                ("max_percentage", models.DecimalField(decimal_places=2, max_digits=5)),
                ("grade_point", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=4)),
                ("remarks", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("-min_percentage",)},
        ),
        migrations.CreateModel(
            name="Exam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=140)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("SCHEDULED", "Scheduled"), ("PUBLISHED", "Published")], default="DRAFT", max_length=20)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="exams", to="core.academicyear")),
                ("semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="exams", to="core.semester")),
            ],
            options={
                "ordering": ("-start_date", "name"),
                "unique_together": {("name", "academic_year", "semester")},
            },
        ),
        migrations.CreateModel(
            name="ExamSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("exam_date", models.DateField()),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("end_time", models.TimeField(blank=True, null=True)),
                ("max_marks", models.DecimalField(decimal_places=2, default=decimal.Decimal("100.00"), max_digits=6)),
                ("pass_marks", models.DecimalField(decimal_places=2, default=decimal.Decimal("40.00"), max_digits=6)),
                ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="exam_schedules", to="academics.teachersubjectassignment")),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="schedules", to="exams.exam")),
            ],
            options={
                "ordering": ("exam_date", "assignment__subject__name"),
                "unique_together": {("exam", "assignment")},
            },
        ),
        migrations.CreateModel(
            name="MarksRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("obtained_marks", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=6)),
                ("remarks", models.CharField(blank=True, max_length=180)),
                ("entered_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="entered_marks", to=settings.AUTH_USER_MODEL)),
                ("schedule", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marks", to="exams.examschedule")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marks_records", to="academics.studentprofile")),
            ],
            options={
                "ordering": ("student__registration_no",),
                "unique_together": {("schedule", "student")},
            },
        ),
        migrations.CreateModel(
            name="Result",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("total_marks", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=8)),
                ("obtained_marks", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=8)),
                ("percentage", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)),
                ("grade", models.CharField(blank=True, max_length=10)),
                ("status", models.CharField(choices=[("PASS", "Pass"), ("FAIL", "Fail")], default="FAIL", max_length=20)),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="exams.exam")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="academics.studentprofile")),
            ],
            options={
                "ordering": ("student__registration_no",),
                "unique_together": {("exam", "student")},
            },
        ),
        migrations.CreateModel(
            name="PromotionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("PROMOTED", "Promoted"), ("REPEAT", "Repeat")], max_length=20)),
                ("remarks", models.CharField(blank=True, max_length=180)),
                ("from_semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="promotions_from", to="core.semester")),
                ("result", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="promotion_record", to="exams.result")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="promotion_records", to="academics.studentprofile")),
                ("to_semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="promotions_to", to="core.semester")),
            ],
            options={"ordering": ("-created_at", "student__registration_no")},
        ),
    ]
