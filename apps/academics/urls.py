from django.urls import path

from . import views


app_name = "academics"

urlpatterns = [
    path("", views.AcademicsHomeView.as_view(), name="home"),
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/create/", views.StudentCreateView.as_view(), name="student_create"),
    path("students/<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("students/<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_update"),
    path("faculty/", views.FacultyListView.as_view(), name="faculty_list"),
    path("faculty/create/", views.FacultyCreateView.as_view(), name="faculty_create"),
    path("faculty/<int:pk>/", views.FacultyDetailView.as_view(), name="faculty_detail"),
    path("faculty/<int:pk>/edit/", views.FacultyUpdateView.as_view(), name="faculty_update"),
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/<int:pk>/edit/", views.CourseUpdateView.as_view(), name="course_update"),
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/create/", views.SubjectCreateView.as_view(), name="subject_create"),
    path("subjects/<int:pk>/", views.SubjectDetailView.as_view(), name="subject_detail"),
    path("subjects/<int:pk>/edit/", views.SubjectUpdateView.as_view(), name="subject_update"),
    path("classes/", views.ClassGroupListView.as_view(), name="classgroup_list"),
    path("classes/create/", views.ClassGroupCreateView.as_view(), name="classgroup_create"),
    path("classes/<int:pk>/", views.ClassGroupDetailView.as_view(), name="classgroup_detail"),
    path("classes/<int:pk>/edit/", views.ClassGroupUpdateView.as_view(), name="classgroup_update"),
    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment_list"),
    path("enrollments/create/", views.EnrollmentCreateView.as_view(), name="enrollment_create"),
    path("enrollments/<int:pk>/", views.EnrollmentDetailView.as_view(), name="enrollment_detail"),
    path("enrollments/<int:pk>/edit/", views.EnrollmentUpdateView.as_view(), name="enrollment_update"),
    path("assignments/", views.AssignmentListView.as_view(), name="assignment_list"),
    path("assignments/create/", views.AssignmentCreateView.as_view(), name="assignment_create"),
    path("assignments/<int:pk>/", views.AssignmentDetailView.as_view(), name="assignment_detail"),
    path("assignments/<int:pk>/edit/", views.AssignmentUpdateView.as_view(), name="assignment_update"),
]
