from django import forms

from apps.academics.models import TeacherSubjectAssignment

from .models import AttendanceRecord, AttendanceSession, Notice


class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ("assignment", "date", "topic", "status")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, teacher_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = TeacherSubjectAssignment.objects.filter(is_active=True).select_related(
            "subject",
            "class_group",
            "academic_year",
            "semester",
            "teacher",
        )
        if teacher_profile is not None:
            queryset = queryset.filter(teacher=teacher_profile)
        self.fields["assignment"].queryset = queryset
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ("title", "body", "audience", "publish_at", "expires_at", "is_active")
        widgets = {
            "publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ("status", "remarks")
