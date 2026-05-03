from django import forms

from apps.accounts.models import User

from .models import (
    ClassGroup,
    Course,
    Enrollment,
    FacultyProfile,
    StudentProfile,
    Subject,
    TeacherSubjectAssignment,
)


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class CourseForm(BaseModelForm):
    class Meta:
        model = Course
        fields = ("name", "code", "department", "duration_semesters", "description", "is_active")


class SubjectForm(BaseModelForm):
    class Meta:
        model = Subject
        fields = ("course", "name", "code", "credit_hours", "semester_number", "is_active")


class ClassGroupForm(BaseModelForm):
    class Meta:
        model = ClassGroup
        fields = ("course", "academic_year", "semester", "name", "section", "is_active")


class StudentProfileForm(BaseModelForm):
    class Meta:
        model = StudentProfile
        fields = (
            "user",
            "registration_no",
            "roll_no",
            "full_name",
            "father_name",
            "department",
            "course",
            "current_class",
            "admission_date",
            "phone",
            "guardian_phone",
            "address",
            "status",
        )
        widgets = {"admission_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(role=User.Roles.STUDENT).order_by("username")


class FacultyProfileForm(BaseModelForm):
    class Meta:
        model = FacultyProfile
        fields = (
            "user",
            "employee_no",
            "full_name",
            "department",
            "designation",
            "qualification",
            "joining_date",
            "phone",
            "address",
            "status",
        )
        widgets = {"joining_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(role=User.Roles.TEACHER).order_by("username")


class EnrollmentForm(BaseModelForm):
    class Meta:
        model = Enrollment
        fields = ("student", "subject", "class_group", "academic_year", "semester", "status")


class TeacherSubjectAssignmentForm(BaseModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ("teacher", "subject", "class_group", "academic_year", "semester", "workload_hours", "is_active")
