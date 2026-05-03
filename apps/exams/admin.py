from django.contrib import admin

from .models import Exam, ExamSchedule, GradeScale, MarksRecord, PromotionRecord, Result


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "min_percentage", "max_percentage", "grade_point", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "remarks")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "semester", "start_date", "end_date", "status", "published_at")
    list_filter = ("academic_year", "semester", "status")
    search_fields = ("name",)


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("exam", "assignment", "exam_date", "max_marks", "pass_marks")
    list_filter = ("exam", "exam_date", "assignment__class_group")
    search_fields = ("exam__name", "assignment__subject__name", "assignment__teacher__full_name")


@admin.register(MarksRecord)
class MarksRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "schedule", "obtained_marks", "entered_by")
    list_filter = ("schedule__exam", "schedule__assignment__subject")
    search_fields = ("student__registration_no", "student__full_name", "schedule__assignment__subject__name")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "obtained_marks", "total_marks", "percentage", "grade", "status", "published_at")
    list_filter = ("exam", "status", "grade")
    search_fields = ("student__registration_no", "student__full_name", "exam__name")


@admin.register(PromotionRecord)
class PromotionRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "from_semester", "to_semester", "status", "result")
    list_filter = ("status", "from_semester", "to_semester")
    search_fields = ("student__registration_no", "student__full_name")
