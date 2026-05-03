from django.conf import settings
from django.db import models

from apps.core.models import AcademicYear, Department, Semester, TimestampedModel


class Course(TimestampedModel):
    name = models.CharField(max_length=140)
    code = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="courses")
    duration_semesters = models.PositiveSmallIntegerField(default=8)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Subject(TimestampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=140)
    code = models.CharField(max_length=30, unique=True)
    credit_hours = models.PositiveSmallIntegerField(default=3)
    semester_number = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("course", "semester_number", "name")

    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassGroup(TimestampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="class_groups")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="class_groups")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="class_groups")
    name = models.CharField(max_length=80)
    section = models.CharField(max_length=20, default="A")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("academic_year", "course", "semester", "section")
        unique_together = ("course", "academic_year", "semester", "section")

    def __str__(self):
        return f"{self.course.code} {self.semester.name} - Section {self.section}"


class StudentProfile(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PASSED_OUT = "PASSED_OUT", "Passed Out"
        LEFT = "LEFT", "Left"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="student_profile",
    )
    registration_no = models.CharField(max_length=50, unique=True)
    roll_no = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=160)
    father_name = models.CharField(max_length=160, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="students")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="students")
    current_class = models.ForeignKey(
        ClassGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="students",
    )
    admission_date = models.DateField()
    phone = models.CharField(max_length=30, blank=True)
    guardian_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ("registration_no",)

    def __str__(self):
        return f"{self.registration_no} - {self.full_name}"


class FacultyProfile(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        INACTIVE = "INACTIVE", "Inactive"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="faculty_profile",
    )
    employee_no = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=160)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="faculty_members")
    designation = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=160, blank=True)
    joining_date = models.DateField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ("full_name",)

    def __str__(self):
        return f"{self.employee_no} - {self.full_name}"


class Enrollment(TimestampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        DROPPED = "DROPPED", "Dropped"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="enrollments")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="enrollments")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ("student", "semester", "subject")
        unique_together = ("student", "subject", "academic_year", "semester")

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}"


class TeacherSubjectAssignment(TimestampedModel):
    teacher = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name="subject_assignments")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="teacher_assignments")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name="teacher_assignments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="teacher_assignments")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="teacher_assignments")
    workload_hours = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("teacher", "semester", "subject")
        unique_together = ("teacher", "subject", "class_group", "academic_year", "semester")

    def __str__(self):
        return f"{self.teacher.full_name} teaches {self.subject.name}"
