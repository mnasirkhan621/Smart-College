from django.urls import path

from . import views


app_name = "exams"

urlpatterns = [
    path("", views.ExamHomeView.as_view(), name="home"),
    path("grades/", views.GradeScaleListView.as_view(), name="grade_list"),
    path("grades/create/", views.GradeScaleCreateView.as_view(), name="grade_create"),
    path("exams/", views.ExamListView.as_view(), name="exam_list"),
    path("exams/create/", views.ExamCreateView.as_view(), name="exam_create"),
    path("schedules/", views.ExamScheduleListView.as_view(), name="schedule_list"),
    path("schedules/create/", views.ExamScheduleCreateView.as_view(), name="schedule_create"),
    path("schedules/<int:pk>/marks/", views.MarksEntryView.as_view(), name="marks_entry"),
    path("publish/<int:exam_id>/", views.PublishResultView.as_view(), name="publish_results"),
    path("results/", views.ResultListView.as_view(), name="result_list"),
    path("results/<int:pk>/", views.ResultDetailView.as_view(), name="result_detail"),
    path("my-results/", views.StudentResultListView.as_view(), name="student_results"),
    path("my-results/<int:pk>/", views.StudentResultDetailView.as_view(), name="student_result_detail"),
]
