from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from apps.accounts.models import User
from apps.academics.models import Enrollment, FacultyProfile, StudentProfile, TeacherSubjectAssignment
from apps.attendance.models import AttendanceRecord, Notice


class HomeView(TemplateView):
    template_name = "core/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)


@login_required
def dashboard(request):
    user = request.user
    context = {
        "notices": [notice for notice in Notice.objects.filter(is_active=True).order_by("-publish_at")[:10] if notice.is_visible_to(user)][:3]
    }
    if user.is_admin_role:
        template = "dashboards/admin.html"
    elif user.role == User.Roles.TEACHER:
        template = "dashboards/teacher.html"
        faculty_profile = FacultyProfile.objects.filter(user=user).first()
        context["faculty_profile"] = faculty_profile
        context["assignments"] = TeacherSubjectAssignment.objects.filter(
            teacher=faculty_profile,
            is_active=True,
        ).select_related("subject", "class_group", "semester", "academic_year") if faculty_profile else []
    else:
        template = "dashboards/student.html"
        student_profile = StudentProfile.objects.filter(user=user).first()
        context["student_profile"] = student_profile
        context["enrollments"] = Enrollment.objects.filter(
            student=student_profile,
            status=Enrollment.Status.ACTIVE,
        ).select_related("subject", "class_group", "semester", "academic_year") if student_profile else []
        if student_profile:
            records = AttendanceRecord.objects.filter(student=student_profile)
            total = records.count()
            present = records.filter(status__in=[AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE]).count()
            context["attendance_percentage"] = round((present / total) * 100, 2) if total else None
    return render(request, template, context)
