from django.contrib import admin

from .models import AttendanceRecord, AttendanceSession, Notice


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    autocomplete_fields = ("student",)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "date", "status", "created_by")
    list_filter = ("status", "date", "assignment__academic_year", "assignment__semester")
    search_fields = ("assignment__subject__name", "assignment__teacher__full_name", "topic")
    inlines = (AttendanceRecordInline,)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "session", "status", "remarks")
    list_filter = ("status", "session__date")
    search_fields = ("student__registration_no", "student__full_name", "session__assignment__subject__name")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "publish_at", "expires_at", "is_active", "created_by")
    list_filter = ("audience", "is_active", "publish_at")
    search_fields = ("title", "body")
