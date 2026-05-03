from django import forms

from apps.academics.models import TeacherSubjectAssignment

from .models import Exam, ExamSchedule, GradeScale


class BaseExamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class GradeScaleForm(BaseExamForm):
    class Meta:
        model = GradeScale
        fields = ("name", "min_percentage", "max_percentage", "grade_point", "remarks", "is_active")


class ExamForm(BaseExamForm):
    class Meta:
        model = Exam
        fields = ("name", "academic_year", "semester", "start_date", "end_date", "status")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class ExamScheduleForm(BaseExamForm):
    class Meta:
        model = ExamSchedule
        fields = ("exam", "assignment", "exam_date", "start_time", "end_time", "max_marks", "pass_marks")
        widgets = {
            "exam_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, teacher_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = TeacherSubjectAssignment.objects.filter(is_active=True).select_related(
            "teacher",
            "subject",
            "class_group",
            "academic_year",
            "semester",
        )
        if teacher_profile is not None:
            queryset = queryset.filter(teacher=teacher_profile)
        self.fields["assignment"].queryset = queryset
