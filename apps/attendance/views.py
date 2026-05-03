from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from apps.academics.models import Enrollment, FacultyProfile, StudentProfile, TeacherSubjectAssignment
from apps.accounts.models import User
from apps.accounts.views import AdminRequiredMixin

from .forms import AttendanceSessionForm, NoticeForm
from .models import AttendanceRecord, AttendanceSession, Notice


class TeacherOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_admin_role or user.role == User.Roles.TEACHER


def visible_notices_for(user):
    notices = Notice.objects.filter(is_active=True).order_by("-publish_at", "-created_at")
    return [notice for notice in notices if notice.is_visible_to(user)]


def session_allowed_for_user(session, user):
    if user.is_admin_role:
        return True
    faculty_profile = FacultyProfile.objects.filter(user=user).first()
    return faculty_profile and session.assignment.teacher_id == faculty_profile.id


def ensure_session_records(session):
    enrollments = Enrollment.objects.filter(
        subject=session.assignment.subject,
        class_group=session.assignment.class_group,
        academic_year=session.assignment.academic_year,
        semester=session.assignment.semester,
        status=Enrollment.Status.ACTIVE,
    ).select_related("student")
    for enrollment in enrollments:
        AttendanceRecord.objects.get_or_create(
            session=session,
            student=enrollment.student,
            defaults={"status": AttendanceRecord.Status.PRESENT},
        )


class AttendanceHomeView(TeacherOrAdminRequiredMixin, TemplateView):
    template_name = "attendance/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["session_count"] = AttendanceSession.objects.count()
        context["notice_count"] = Notice.objects.filter(is_active=True).count()
        return context


class AttendanceSessionListView(TeacherOrAdminRequiredMixin, ListView):
    model = AttendanceSession
    template_name = "attendance/session_list.html"
    context_object_name = "sessions"
    paginate_by = 25

    def get_queryset(self):
        queryset = AttendanceSession.objects.select_related(
            "assignment__teacher",
            "assignment__subject",
            "assignment__class_group",
            "created_by",
        )
        if self.request.user.is_admin_role:
            return queryset
        faculty_profile = FacultyProfile.objects.filter(user=self.request.user).first()
        if not faculty_profile:
            return queryset.none()
        return queryset.filter(assignment__teacher=faculty_profile)


class AttendanceSessionCreateView(TeacherOrAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = AttendanceSession
    form_class = AttendanceSessionForm
    template_name = "attendance/session_form.html"
    success_message = "Attendance session created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.request.user.is_admin_role:
            kwargs["teacher_profile"] = FacultyProfile.objects.filter(user=self.request.user).first()
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        ensure_session_records(self.object)
        return response

    def get_success_url(self):
        return reverse("attendance:mark", args=[self.object.pk])


class AttendanceMarkView(TeacherOrAdminRequiredMixin, View):
    template_name = "attendance/mark.html"

    def get_session(self):
        session = get_object_or_404(
            AttendanceSession.objects.select_related(
                "assignment__teacher",
                "assignment__subject",
                "assignment__class_group",
                "assignment__academic_year",
                "assignment__semester",
            ),
            pk=self.kwargs["pk"],
        )
        if not session_allowed_for_user(session, self.request.user):
            return None
        ensure_session_records(session)
        return session

    def get(self, request, *args, **kwargs):
        session = self.get_session()
        if not session:
            messages.error(request, "You do not have access to this attendance session.")
            return redirect("attendance:session_list")
        records = session.records.select_related("student").all()
        from django.shortcuts import render

        return render(request, self.template_name, {"session": session, "records": records, "statuses": AttendanceRecord.Status.choices})

    def post(self, request, *args, **kwargs):
        session = self.get_session()
        if not session:
            messages.error(request, "You do not have access to this attendance session.")
            return redirect("attendance:session_list")
        for record in session.records.all():
            status = request.POST.get(f"status_{record.id}", record.status)
            remarks = request.POST.get(f"remarks_{record.id}", "")
            if status in AttendanceRecord.Status.values:
                record.status = status
                record.remarks = remarks
                record.save(update_fields=["status", "remarks", "updated_at"])
        session.status = AttendanceSession.Status.SUBMITTED
        session.save(update_fields=["status", "updated_at"])
        messages.success(request, "Attendance saved.")
        return redirect("attendance:session_list")


class StudentAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/student_attendance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = StudentProfile.objects.filter(user=self.request.user).first()
        context["student_profile"] = student_profile
        if not student_profile:
            context["records"] = []
            context["summary"] = []
            return context
        records = AttendanceRecord.objects.filter(student=student_profile).select_related(
            "session__assignment__subject",
            "session__assignment__class_group",
        )
        summary = records.values("session__assignment__subject__name").annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status__in=[AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE])),
        ).order_by("session__assignment__subject__name")
        context["records"] = records
        context["summary"] = [
            {
                "subject": item["session__assignment__subject__name"],
                "total": item["total"],
                "present": item["present"],
                "percentage": round((item["present"] / item["total"]) * 100, 2) if item["total"] else 0,
            }
            for item in summary
        ]
        return context


class LowAttendanceReportView(AdminRequiredMixin, TemplateView):
    template_name = "attendance/low_attendance.html"
    threshold = 75

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = []
        for student in StudentProfile.objects.filter(status=StudentProfile.Status.ACTIVE).select_related("course", "current_class"):
            records = AttendanceRecord.objects.filter(student=student)
            total = records.count()
            present = records.filter(status__in=[AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE]).count()
            percentage = round((present / total) * 100, 2) if total else 0
            if total and percentage < self.threshold:
                rows.append({"student": student, "total": total, "present": present, "percentage": percentage})
        context["rows"] = rows
        context["threshold"] = self.threshold
        return context


class NoticeListView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/notice_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notices"] = visible_notices_for(self.request.user)
        return context


class NoticeCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Notice
    form_class = NoticeForm
    template_name = "attendance/notice_form.html"
    success_url = reverse_lazy("attendance:notice_list")
    success_message = "Notice published."

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
