from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    # TASK: submit path
    # Handles the exam form POST, creates the Submission, then
    # redirects to the exam_result path below.
    path('<int:course_id>/submit/', views.submit, name='submit'),

    # TASK: show_exam_result path
    # Displays the graded result for one submission.
    path(
        '<int:course_id>/submission/<int:submission_id>/result/',
        views.show_exam_result,
        name='exam_result'
    ),
]
