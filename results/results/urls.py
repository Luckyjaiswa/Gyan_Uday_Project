from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('',                              views.exam_list,          name='list'),
    path('marks/',                        views.marks_list,         name='marks'),
    path('create/',                       views.exam_create,        name='exam_create'),
    path('<int:pk>/',                     views.exam_detail,        name='exam_detail'),
    path('<int:exam_pk>/enter-marks/',    views.bulk_mark_entry,    name='bulk_mark_entry'),
    path('student/<int:student_pk>/',     views.student_result_card,name='student_result_card'),
    path('activity/',                     views.activity_log,       name='activity_log'),
]
