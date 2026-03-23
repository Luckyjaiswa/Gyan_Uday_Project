from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('',                              views.attendance_list,  name='list'),
    path('mark/',                         views.bulk_mark,        name='bulk_mark'),
    path('student/<int:student_pk>/',     views.student_report,   name='student_report'),
    path('course/<int:course_pk>/',       views.course_summary,   name='course_summary'),
]
