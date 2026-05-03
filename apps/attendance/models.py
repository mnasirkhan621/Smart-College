from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.academics.models import StudentProfile, TeacherSubjectAssignment
from apps.core.models import TimestampedModel


class AttendanceSession(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"

    assignment = models.ForeignKey(
        TeacherSubjectAssignment,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    date = models.DateField(default=timezone.localdate)
    topic = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_attendance_sessions",
    )

    class Meta:
        ordering = ("-date", "-created_at")
        unique_together = ("assignment", "date")

    def __str__(self):
        return f"{self.assignment.subject.name} attendance on {self.date}"


class AttendanceRecord(TimestampedModel):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        LEAVE = "LEAVE", "Leave"

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    remarks = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ("student__registration_no",)
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student.full_name} - {self.get_status_display()}"

    @property
    def counts_as_present(self):
        return self.status in {self.Status.PRESENT, self.Status.LATE}


class Notice(TimestampedModel):
    class Audience(models.TextChoices):
        ALL = "ALL", "All Users"
        ADMINS = "ADMINS", "Admins"
        TEACHERS = "TEACHERS", "Teachers"
        STUDENTS = "STUDENTS", "Students"

    title = models.CharField(max_length=180)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL)
    publish_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_notices",
    )

    class Meta:
        ordering = ("-publish_at", "-created_at")

    def __str__(self):
        return self.title

    def is_visible_to(self, user):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.publish_at > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        if self.audience == self.Audience.ALL:
            return True
        if self.audience == self.Audience.ADMINS:
            return user.is_admin_role
        if self.audience == self.Audience.TEACHERS:
            return user.is_teacher_role
        if self.audience == self.Audience.STUDENTS:
            return user.is_student_role
        return False
