import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=140)),
                ("code", models.CharField(max_length=30, unique=True)),
                ("duration_semesters", models.PositiveSmallIntegerField(default=8)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="courses", to="core.department")),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="FacultyProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("employee_no", models.CharField(max_length=50, unique=True)),
                ("full_name", models.CharField(max_length=160)),
                ("designation", models.CharField(blank=True, max_length=100)),
                ("qualification", models.CharField(blank=True, max_length=160)),
                ("joining_date", models.DateField()),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("address", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("ON_LEAVE", "On Leave"), ("INACTIVE", "Inactive")], default="ACTIVE", max_length=20)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="faculty_members", to="core.department")),
                ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="faculty_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("full_name",)},
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=140)),
                ("code", models.CharField(max_length=30, unique=True)),
                ("credit_hours", models.PositiveSmallIntegerField(default=3)),
                ("semester_number", models.PositiveSmallIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subjects", to="academics.course")),
            ],
            options={"ordering": ("course", "semester_number", "name")},
        ),
        migrations.CreateModel(
            name="ClassGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80)),
                ("section", models.CharField(default="A", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_groups", to="core.academicyear")),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="class_groups", to="academics.course")),
                ("semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_groups", to="core.semester")),
            ],
            options={
                "ordering": ("academic_year", "course", "semester", "section"),
                "unique_together": {("course", "academic_year", "semester", "section")},
            },
        ),
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("registration_no", models.CharField(max_length=50, unique=True)),
                ("roll_no", models.CharField(blank=True, max_length=50)),
                ("full_name", models.CharField(max_length=160)),
                ("father_name", models.CharField(blank=True, max_length=160)),
                ("admission_date", models.DateField()),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("guardian_phone", models.CharField(blank=True, max_length=30)),
                ("address", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("PASSED_OUT", "Passed Out"), ("LEFT", "Left"), ("SUSPENDED", "Suspended")], default="ACTIVE", max_length=20)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="students", to="academics.course")),
                ("current_class", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="academics.classgroup")),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="students", to="core.department")),
                ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="student_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("registration_no",)},
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("COMPLETED", "Completed"), ("DROPPED", "Dropped")], default="ACTIVE", max_length=20)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="core.academicyear")),
                ("class_group", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="academics.classgroup")),
                ("semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="core.semester")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="academics.studentprofile")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="academics.subject")),
            ],
            options={
                "ordering": ("student", "semester", "subject"),
                "unique_together": {("student", "subject", "academic_year", "semester")},
            },
        ),
        migrations.CreateModel(
            name="TeacherSubjectAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("workload_hours", models.PositiveSmallIntegerField(default=3)),
                ("is_active", models.BooleanField(default=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="teacher_assignments", to="core.academicyear")),
                ("class_group", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="teacher_assignments", to="academics.classgroup")),
                ("semester", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="teacher_assignments", to="core.semester")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="teacher_assignments", to="academics.subject")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subject_assignments", to="academics.facultyprofile")),
            ],
            options={
                "ordering": ("teacher", "semester", "subject"),
                "unique_together": {("teacher", "subject", "class_group", "academic_year", "semester")},
            },
        ),
    ]
