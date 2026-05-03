from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from apps.accounts.views import AdminRequiredMixin

from .forms import (
    ClassGroupForm,
    CourseForm,
    EnrollmentForm,
    FacultyProfileForm,
    StudentProfileForm,
    SubjectForm,
    TeacherSubjectAssignmentForm,
)
from .models import (
    ClassGroup,
    Course,
    Enrollment,
    FacultyProfile,
    StudentProfile,
    Subject,
    TeacherSubjectAssignment,
)


def resolve_attr(obj, attr):
    value = obj
    for part in attr.split("__"):
        value = getattr(value, part, None)
        if value is None:
            return "-"
    if callable(value):
        value = value()
    return value if value not in {"", None} else "-"


class AcademicsHomeView(AdminRequiredMixin, TemplateView):
    template_name = "academics/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = [
            ("Students", StudentProfile.objects.count(), "academics:student_list"),
            ("Faculty", FacultyProfile.objects.count(), "academics:faculty_list"),
            ("Courses", Course.objects.count(), "academics:course_list"),
            ("Subjects", Subject.objects.count(), "academics:subject_list"),
            ("Classes", ClassGroup.objects.count(), "academics:classgroup_list"),
            ("Enrollments", Enrollment.objects.count(), "academics:enrollment_list"),
            ("Assignments", TeacherSubjectAssignment.objects.count(), "academics:assignment_list"),
        ]
        return context


class AcademicListView(AdminRequiredMixin, ListView):
    template_name = "academics/object_list.html"
    paginate_by = 25
    columns = ()
    title = ""
    create_url_name = ""
    detail_url_name = ""
    update_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["create_url"] = reverse(self.create_url_name)
        context["headers"] = [label for label, _ in self.columns]
        rows = []
        for item in context["object_list"]:
            rows.append(
                {
                    "object": item,
                    "detail_url": reverse(self.detail_url_name, args=[item.pk]),
                    "update_url": reverse(self.update_url_name, args=[item.pk]),
                    "values": [resolve_attr(item, attr) for _, attr in self.columns],
                }
            )
        context["rows"] = rows
        return context


class AcademicDetailView(AdminRequiredMixin, DetailView):
    template_name = "academics/object_detail.html"
    title = ""
    fields = ()
    update_url_name = ""
    list_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["update_url"] = reverse(self.update_url_name, args=[self.object.pk])
        context["list_url"] = reverse(self.list_url_name)
        context["fields"] = [(label, resolve_attr(self.object, attr)) for label, attr in self.fields]
        return context


class AcademicFormView(AdminRequiredMixin, SuccessMessageMixin):
    template_name = "academics/object_form.html"
    title = ""
    success_message = "Academic record saved."
    list_url_name = ""

    def get_success_url(self):
        return reverse(self.list_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["list_url"] = reverse(self.list_url_name)
        return context


class StudentListView(AcademicListView):
    model = StudentProfile
    title = "Students"
    create_url_name = "academics:student_create"
    detail_url_name = "academics:student_detail"
    update_url_name = "academics:student_update"
    columns = (
        ("Registration No", "registration_no"),
        ("Name", "full_name"),
        ("Course", "course"),
        ("Class", "current_class"),
        ("Status", "get_status_display"),
    )

    def get_queryset(self):
        return StudentProfile.objects.select_related("course", "current_class", "department")


class StudentDetailView(AcademicDetailView):
    model = StudentProfile
    title = "Student Details"
    update_url_name = "academics:student_update"
    list_url_name = "academics:student_list"
    fields = (
        ("Registration No", "registration_no"),
        ("Roll No", "roll_no"),
        ("Name", "full_name"),
        ("Father Name", "father_name"),
        ("Department", "department"),
        ("Course", "course"),
        ("Current Class", "current_class"),
        ("Admission Date", "admission_date"),
        ("Phone", "phone"),
        ("Guardian Phone", "guardian_phone"),
        ("Address", "address"),
        ("Status", "get_status_display"),
    )


class StudentCreateView(AcademicFormView, CreateView):
    model = StudentProfile
    form_class = StudentProfileForm
    title = "Create Student"
    list_url_name = "academics:student_list"


class StudentUpdateView(AcademicFormView, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    title = "Edit Student"
    list_url_name = "academics:student_list"


class FacultyListView(AcademicListView):
    model = FacultyProfile
    title = "Faculty"
    create_url_name = "academics:faculty_create"
    detail_url_name = "academics:faculty_detail"
    update_url_name = "academics:faculty_update"
    columns = (
        ("Employee No", "employee_no"),
        ("Name", "full_name"),
        ("Department", "department"),
        ("Designation", "designation"),
        ("Status", "get_status_display"),
    )

    def get_queryset(self):
        return FacultyProfile.objects.select_related("department")


class FacultyDetailView(AcademicDetailView):
    model = FacultyProfile
    title = "Faculty Details"
    update_url_name = "academics:faculty_update"
    list_url_name = "academics:faculty_list"
    fields = (
        ("Employee No", "employee_no"),
        ("Name", "full_name"),
        ("Department", "department"),
        ("Designation", "designation"),
        ("Qualification", "qualification"),
        ("Joining Date", "joining_date"),
        ("Phone", "phone"),
        ("Address", "address"),
        ("Status", "get_status_display"),
    )


class FacultyCreateView(AcademicFormView, CreateView):
    model = FacultyProfile
    form_class = FacultyProfileForm
    title = "Create Faculty"
    list_url_name = "academics:faculty_list"


class FacultyUpdateView(AcademicFormView, UpdateView):
    model = FacultyProfile
    form_class = FacultyProfileForm
    title = "Edit Faculty"
    list_url_name = "academics:faculty_list"


class CourseListView(AcademicListView):
    model = Course
    title = "Courses"
    create_url_name = "academics:course_create"
    detail_url_name = "academics:course_detail"
    update_url_name = "academics:course_update"
    columns = (("Code", "code"), ("Name", "name"), ("Department", "department"), ("Semesters", "duration_semesters"), ("Active", "is_active"))

    def get_queryset(self):
        return Course.objects.select_related("department")


class CourseDetailView(AcademicDetailView):
    model = Course
    title = "Course Details"
    update_url_name = "academics:course_update"
    list_url_name = "academics:course_list"
    fields = (("Code", "code"), ("Name", "name"), ("Department", "department"), ("Semesters", "duration_semesters"), ("Description", "description"), ("Active", "is_active"))


class CourseCreateView(AcademicFormView, CreateView):
    model = Course
    form_class = CourseForm
    title = "Create Course"
    list_url_name = "academics:course_list"


class CourseUpdateView(AcademicFormView, UpdateView):
    model = Course
    form_class = CourseForm
    title = "Edit Course"
    list_url_name = "academics:course_list"


class SubjectListView(AcademicListView):
    model = Subject
    title = "Subjects"
    create_url_name = "academics:subject_create"
    detail_url_name = "academics:subject_detail"
    update_url_name = "academics:subject_update"
    columns = (("Code", "code"), ("Name", "name"), ("Course", "course"), ("Semester", "semester_number"), ("Credit Hours", "credit_hours"))

    def get_queryset(self):
        return Subject.objects.select_related("course")


class SubjectDetailView(AcademicDetailView):
    model = Subject
    title = "Subject Details"
    update_url_name = "academics:subject_update"
    list_url_name = "academics:subject_list"
    fields = (("Code", "code"), ("Name", "name"), ("Course", "course"), ("Semester", "semester_number"), ("Credit Hours", "credit_hours"), ("Active", "is_active"))


class SubjectCreateView(AcademicFormView, CreateView):
    model = Subject
    form_class = SubjectForm
    title = "Create Subject"
    list_url_name = "academics:subject_list"


class SubjectUpdateView(AcademicFormView, UpdateView):
    model = Subject
    form_class = SubjectForm
    title = "Edit Subject"
    list_url_name = "academics:subject_list"


class ClassGroupListView(AcademicListView):
    model = ClassGroup
    title = "Classes"
    create_url_name = "academics:classgroup_create"
    detail_url_name = "academics:classgroup_detail"
    update_url_name = "academics:classgroup_update"
    columns = (("Name", "name"), ("Course", "course"), ("Semester", "semester"), ("Section", "section"), ("Academic Year", "academic_year"))

    def get_queryset(self):
        return ClassGroup.objects.select_related("course", "academic_year", "semester")


class ClassGroupDetailView(AcademicDetailView):
    model = ClassGroup
    title = "Class Details"
    update_url_name = "academics:classgroup_update"
    list_url_name = "academics:classgroup_list"
    fields = (("Name", "name"), ("Course", "course"), ("Academic Year", "academic_year"), ("Semester", "semester"), ("Section", "section"), ("Active", "is_active"))


class ClassGroupCreateView(AcademicFormView, CreateView):
    model = ClassGroup
    form_class = ClassGroupForm
    title = "Create Class"
    list_url_name = "academics:classgroup_list"


class ClassGroupUpdateView(AcademicFormView, UpdateView):
    model = ClassGroup
    form_class = ClassGroupForm
    title = "Edit Class"
    list_url_name = "academics:classgroup_list"


class EnrollmentListView(AcademicListView):
    model = Enrollment
    title = "Enrollments"
    create_url_name = "academics:enrollment_create"
    detail_url_name = "academics:enrollment_detail"
    update_url_name = "academics:enrollment_update"
    columns = (("Student", "student"), ("Subject", "subject"), ("Class", "class_group"), ("Semester", "semester"), ("Status", "get_status_display"))

    def get_queryset(self):
        return Enrollment.objects.select_related("student", "subject", "class_group", "semester", "academic_year")


class EnrollmentDetailView(AcademicDetailView):
    model = Enrollment
    title = "Enrollment Details"
    update_url_name = "academics:enrollment_update"
    list_url_name = "academics:enrollment_list"
    fields = (("Student", "student"), ("Subject", "subject"), ("Class", "class_group"), ("Academic Year", "academic_year"), ("Semester", "semester"), ("Status", "get_status_display"))


class EnrollmentCreateView(AcademicFormView, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    title = "Create Enrollment"
    list_url_name = "academics:enrollment_list"


class EnrollmentUpdateView(AcademicFormView, UpdateView):
    model = Enrollment
    form_class = EnrollmentForm
    title = "Edit Enrollment"
    list_url_name = "academics:enrollment_list"


class AssignmentListView(AcademicListView):
    model = TeacherSubjectAssignment
    title = "Teacher Assignments"
    create_url_name = "academics:assignment_create"
    detail_url_name = "academics:assignment_detail"
    update_url_name = "academics:assignment_update"
    columns = (("Teacher", "teacher"), ("Subject", "subject"), ("Class", "class_group"), ("Semester", "semester"), ("Hours", "workload_hours"))

    def get_queryset(self):
        return TeacherSubjectAssignment.objects.select_related("teacher", "subject", "class_group", "semester", "academic_year")


class AssignmentDetailView(AcademicDetailView):
    model = TeacherSubjectAssignment
    title = "Assignment Details"
    update_url_name = "academics:assignment_update"
    list_url_name = "academics:assignment_list"
    fields = (("Teacher", "teacher"), ("Subject", "subject"), ("Class", "class_group"), ("Academic Year", "academic_year"), ("Semester", "semester"), ("Workload Hours", "workload_hours"), ("Active", "is_active"))


class AssignmentCreateView(AcademicFormView, CreateView):
    model = TeacherSubjectAssignment
    form_class = TeacherSubjectAssignmentForm
    title = "Create Teacher Assignment"
    list_url_name = "academics:assignment_list"


class AssignmentUpdateView(AcademicFormView, UpdateView):
    model = TeacherSubjectAssignment
    form_class = TeacherSubjectAssignmentForm
    title = "Edit Teacher Assignment"
    list_url_name = "academics:assignment_list"
