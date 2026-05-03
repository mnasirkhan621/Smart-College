from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AcademicYear",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=20, unique=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("-start_date",)},
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="SystemSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("key", models.CharField(max_length=80, unique=True)),
                ("value", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ("key",)},
        ),
        migrations.CreateModel(
            name="Semester",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=60)),
                ("number", models.PositiveSmallIntegerField()),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="semesters", to="core.academicyear")),
            ],
            options={
                "ordering": ("academic_year", "number"),
                "unique_together": {("academic_year", "number")},
            },
        ),
    ]
