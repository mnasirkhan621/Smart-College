from django.contrib import admin

from .models import AcademicYear, Department, Semester, SystemSetting


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "number", "academic_year", "is_active")
    list_filter = ("academic_year", "is_active")
    search_fields = ("name", "academic_year__name")


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at")
    search_fields = ("key", "value", "description")
