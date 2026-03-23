from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('',                              views.course_list,       name='list'),
    path('create/',                       views.course_create,     name='create'),
    path('<int:pk>/',                     views.course_detail,     name='detail'),
    path('<int:pk>/edit/',                views.course_update,     name='update'),
    path('<int:course_pk>/enroll/',       views.enrollment_create, name='enroll'),
]
