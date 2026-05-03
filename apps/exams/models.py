from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.academics.models import StudentProfile, TeacherSubjectAssignment
from apps.core.models import AcademicYear, Semester, TimestampedModel


class GradeScale(TimestampedModel):
    name = models.CharField(max_length=40, unique=True)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    remarks = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-min_percentage",)

    def __str__(self):
        return self.name


class Exam(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SCHEDULED = "SCHEDULED", "Scheduled"
        PUBLISHED = "PUBLISHED", "Published"

    name = models.CharField(max_length=140)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="exams")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="exams")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-start_date", "name")
        unique_together = ("name", "academic_year", "semester")

    def __str__(self):
        return f"{self.name} - {self.semester}"


class ExamSchedule(TimestampedModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="schedules")
    assignment = models.ForeignKey(TeacherSubjectAssignment, on_delete=models.PROTECT, related_name="exam_schedules")
    exam_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("100.00"))
    pass_marks = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("40.00"))

    class Meta:
        ordering = ("exam_date", "assignment__subject__name")
        unique_together = ("exam", "assignment")

    def __str__(self):
        return f"{self.exam.name} - {self.assignment.subject.name}"


class MarksRecord(TimestampedModel):
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="marks")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="marks_records")
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    remarks = models.CharField(max_length=180, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="entered_marks",
    )

    class Meta:
        ordering = ("student__registration_no",)
        unique_together = ("schedule", "student")

    def __str__(self):
        return f"{self.student.full_name} - {self.schedule.assignment.subject.name}"

    @property
    def percentage(self):
        if not self.schedule.max_marks:
            return Decimal("0.00")
        return (self.obtained_marks / self.schedule.max_marks) * Decimal("100.00")

    @property
    def is_passed(self):
        return self.obtained_marks >= self.schedule.pass_marks


class Result(TimestampedModel):
    class Status(models.TextChoices):
        PASS = "PASS", "Pass"
        FAIL = "FAIL", "Fail"

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="results")
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    obtained_marks = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    grade = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FAIL)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("student__registration_no",)
        unique_together = ("exam", "student")

    def __str__(self):
        return f"{self.student.full_name} - {self.exam.name}"


class PromotionRecord(TimestampedModel):
    class Status(models.TextChoices):
        PROMOTED = "PROMOTED", "Promoted"
        REPEAT = "REPEAT", "Repeat"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="promotion_records")
    from_semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="promotions_from")
    to_semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="promotions_to")
    result = models.OneToOneField(Result, on_delete=models.CASCADE, related_name="promotion_record")
    status = models.CharField(max_length=20, choices=Status.choices)
    remarks = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ("-created_at", "student__registration_no")

    def __str__(self):
        return f"{self.student.full_name} - {self.get_status_display()}"
