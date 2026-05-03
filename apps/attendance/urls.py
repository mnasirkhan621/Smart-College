from django.urls import path

from . import views


app_name = "attendance"

urlpatterns = [
    path("", views.AttendanceHomeView.as_view(), name="home"),
    path("sessions/", views.AttendanceSessionListView.as_view(), name="session_list"),
    path("sessions/create/", views.AttendanceSessionCreateView.as_view(), name="session_create"),
    path("sessions/<int:pk>/mark/", views.AttendanceMarkView.as_view(), name="mark"),
    path("student/", views.StudentAttendanceView.as_view(), name="student_attendance"),
    path("low-attendance/", views.LowAttendanceReportView.as_view(), name="low_attendance"),
    path("notices/", views.NoticeListView.as_view(), name="notice_list"),
    path("notices/create/", views.NoticeCreateView.as_view(), name="notice_create"),
]
