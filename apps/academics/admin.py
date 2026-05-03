from django.contrib import admin

from .models import (
    ClassGroup,
    Course,
    Enrollment,
    FacultyProfile,
    StudentProfile,
    Subject,
    TeacherSubjectAssignment,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department", "duration_semesters", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("code", "name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "course", "semester_number", "credit_hours", "is_active")
    list_filter = ("course", "semester_number", "is_active")
    search_fields = ("code", "name", "course__name")


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "academic_year", "semester", "section", "is_active")
    list_filter = ("course", "academic_year", "semester", "is_active")
    search_fields = ("name", "section", "course__name")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("registration_no", "full_name", "course", "current_class", "status")
    list_filter = ("department", "course", "current_class", "status")
    search_fields = ("registration_no", "roll_no", "full_name", "father_name")


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ("employee_no", "full_name", "department", "designation", "status")
    list_filter = ("department", "status")
    search_fields = ("employee_no", "full_name", "designation")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "class_group", "semester", "academic_year", "status")
    list_filter = ("academic_year", "semester", "class_group", "status")
    search_fields = ("student__registration_no", "student__full_name", "subject__name")


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "class_group", "semester", "academic_year", "workload_hours", "is_active")
    list_filter = ("academic_year", "semester", "class_group", "is_active")
    search_fields = ("teacher__full_name", "subject__name", "class_group__name")
