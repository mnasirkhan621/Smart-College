from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from apps.academics.models import Enrollment, FacultyProfile, StudentProfile
from apps.accounts.models import User
from apps.accounts.views import AdminRequiredMixin

from .forms import ExamForm, ExamScheduleForm, GradeScaleForm
from .models import Exam, ExamSchedule, GradeScale, MarksRecord, PromotionRecord, Result


class TeacherOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_admin_role or user.role == User.Roles.TEACHER


def schedule_allowed_for_user(schedule, user):
    if user.is_admin_role:
        return True
    faculty_profile = FacultyProfile.objects.filter(user=user).first()
    return faculty_profile and schedule.assignment.teacher_id == faculty_profile.id


def ensure_marks_records(schedule):
    enrollments = Enrollment.objects.filter(
        subject=schedule.assignment.subject,
        class_group=schedule.assignment.class_group,
        academic_year=schedule.assignment.academic_year,
        semester=schedule.assignment.semester,
        status=Enrollment.Status.ACTIVE,
    ).select_related("student")
    for enrollment in enrollments:
        MarksRecord.objects.get_or_create(schedule=schedule, student=enrollment.student)


def grade_for_percentage(percentage):
    grade = GradeScale.objects.filter(
        is_active=True,
        min_percentage__lte=percentage,
        max_percentage__gte=percentage,
    ).order_by("-min_percentage").first()
    return grade.name if grade else ""


def publish_exam_results(exam):
    schedules = exam.schedules.select_related("assignment__subject", "assignment__semester")
    student_ids = MarksRecord.objects.filter(schedule__exam=exam).values_list("student_id", flat=True).distinct()
    created_results = []
    for student in StudentProfile.objects.filter(id__in=student_ids):
        marks = MarksRecord.objects.filter(schedule__exam=exam, student=student).select_related("schedule")
        total_marks = sum((item.schedule.max_marks for item in marks), Decimal("0.00"))
        obtained_marks = sum((item.obtained_marks for item in marks), Decimal("0.00"))
        has_failed_subject = any(not item.is_passed for item in marks)
        has_missing_subjects = marks.count() < schedules.count()
        percentage = (obtained_marks / total_marks * Decimal("100.00")) if total_marks else Decimal("0.00")
        status = Result.Status.FAIL if has_failed_subject or has_missing_subjects else Result.Status.PASS
        result, _ = Result.objects.update_or_create(
            exam=exam,
            student=student,
            defaults={
                "total_marks": total_marks,
                "obtained_marks": obtained_marks,
                "percentage": percentage,
                "grade": grade_for_percentage(percentage),
                "status": status,
                "published_at": timezone.now(),
            },
        )
        PromotionRecord.objects.update_or_create(
            result=result,
            defaults={
                "student": student,
                "from_semester": exam.semester,
                "to_semester": exam.semester,
                "status": PromotionRecord.Status.PROMOTED if status == Result.Status.PASS else PromotionRecord.Status.REPEAT,
                "remarks": "Auto-generated from published result.",
            },
        )
        created_results.append(result)
    exam.status = Exam.Status.PUBLISHED
    exam.published_at = timezone.now()
    exam.save(update_fields=["status", "published_at", "updated_at"])
    return created_results


class ExamHomeView(TeacherOrAdminRequiredMixin, TemplateView):
    template_name = "exams/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exam_count"] = Exam.objects.count()
        context["schedule_count"] = ExamSchedule.objects.count()
        context["result_count"] = Result.objects.count()
        return context


class GradeScaleListView(AdminRequiredMixin, ListView):
    model = GradeScale
    template_name = "exams/grade_list.html"
    context_object_name = "grades"


class GradeScaleCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = GradeScale
    form_class = GradeScaleForm
    template_name = "exams/form.html"
    success_url = reverse_lazy("exams:grade_list")
    success_message = "Grade scale saved."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Grade Scale"
        context["cancel_url"] = reverse("exams:grade_list")
        return context


class ExamListView(TeacherOrAdminRequiredMixin, ListView):
    model = Exam
    template_name = "exams/exam_list.html"
    context_object_name = "exams"


class ExamCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "exams/form.html"
    success_url = reverse_lazy("exams:exam_list")
    success_message = "Exam saved."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Exam"
        context["cancel_url"] = reverse("exams:exam_list")
        return context


class ExamScheduleListView(TeacherOrAdminRequiredMixin, ListView):
    model = ExamSchedule
    template_name = "exams/schedule_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        queryset = ExamSchedule.objects.select_related(
            "exam",
            "assignment__teacher",
            "assignment__subject",
            "assignment__class_group",
        )
        if self.request.user.is_admin_role:
            return queryset
        faculty_profile = FacultyProfile.objects.filter(user=self.request.user).first()
        if not faculty_profile:
            return queryset.none()
        return queryset.filter(assignment__teacher=faculty_profile)


class ExamScheduleCreateView(TeacherOrAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExamSchedule
    form_class = ExamScheduleForm
    template_name = "exams/form.html"
    success_message = "Exam schedule saved."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.request.user.is_admin_role:
            kwargs["teacher_profile"] = FacultyProfile.objects.filter(user=self.request.user).first()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Exam Schedule"
        context["cancel_url"] = reverse("exams:schedule_list")
        return context

    def get_success_url(self):
        return reverse("exams:marks_entry", args=[self.object.pk])


class MarksEntryView(TeacherOrAdminRequiredMixin, View):
    template_name = "exams/marks_entry.html"

    def get_schedule(self):
        schedule = get_object_or_404(
            ExamSchedule.objects.select_related(
                "exam",
                "assignment__teacher",
                "assignment__subject",
                "assignment__class_group",
            ),
            pk=self.kwargs["pk"],
        )
        if not schedule_allowed_for_user(schedule, self.request.user):
            return None
        ensure_marks_records(schedule)
        return schedule

    def get(self, request, *args, **kwargs):
        schedule = self.get_schedule()
        if not schedule:
            messages.error(request, "You do not have access to this marks sheet.")
            return redirect("exams:schedule_list")
        records = schedule.marks.select_related("student").all()
        return render(request, self.template_name, {"schedule": schedule, "records": records})

    def post(self, request, *args, **kwargs):
        schedule = self.get_schedule()
        if not schedule:
            messages.error(request, "You do not have access to this marks sheet.")
            return redirect("exams:schedule_list")
        for record in schedule.marks.all():
            value = request.POST.get(f"marks_{record.id}", record.obtained_marks)
            remarks = request.POST.get(f"remarks_{record.id}", "")
            try:
                marks = Decimal(value)
            except Exception:
                marks = record.obtained_marks
            if marks < 0:
                marks = Decimal("0.00")
            if marks > schedule.max_marks:
                marks = schedule.max_marks
            record.obtained_marks = marks
            record.remarks = remarks
            record.entered_by = request.user
            record.save(update_fields=["obtained_marks", "remarks", "entered_by", "updated_at"])
        messages.success(request, "Marks saved.")
        return redirect("exams:schedule_list")


class PublishResultView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs["exam_id"])
        for schedule in exam.schedules.all():
            ensure_marks_records(schedule)
        results = publish_exam_results(exam)
        messages.success(request, f"Published {len(results)} result(s).")
        return redirect("exams:result_list")


class ResultListView(AdminRequiredMixin, ListView):
    model = Result
    template_name = "exams/result_list.html"
    context_object_name = "results"

    def get_queryset(self):
        return Result.objects.select_related("exam", "student", "student__course")


class ResultDetailView(AdminRequiredMixin, DetailView):
    model = Result
    template_name = "exams/result_detail.html"
    context_object_name = "result"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marks"] = MarksRecord.objects.filter(
            schedule__exam=self.object.exam,
            student=self.object.student,
        ).select_related("schedule__assignment__subject")
        return context


class StudentResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = "exams/student_results.html"
    context_object_name = "results"

    def get_queryset(self):
        student_profile = StudentProfile.objects.filter(user=self.request.user).first()
        if not student_profile:
            return Result.objects.none()
        return Result.objects.filter(student=student_profile, exam__status=Exam.Status.PUBLISHED).select_related("exam")


class StudentResultDetailView(LoginRequiredMixin, DetailView):
    model = Result
    template_name = "exams/result_detail.html"
    context_object_name = "result"

    def get_queryset(self):
        student_profile = StudentProfile.objects.filter(user=self.request.user).first()
        if not student_profile:
            return Result.objects.none()
        return Result.objects.filter(student=student_profile, exam__status=Exam.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marks"] = MarksRecord.objects.filter(
            schedule__exam=self.object.exam,
            student=self.object.student,
        ).select_related("schedule__assignment__subject")
        return context
