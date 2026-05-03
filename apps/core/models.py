from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(TimestampedModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class AcademicYear(TimestampedModel):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return self.name


class Semester(TimestampedModel):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="semesters")
    name = models.CharField(max_length=60)
    number = models.PositiveSmallIntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("academic_year", "number")
        ordering = ("academic_year", "number")

    def __str__(self):
        return f"{self.name} - {self.academic_year}"


class SystemSetting(TimestampedModel):
    key = models.CharField(max_length=80, unique=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.key
