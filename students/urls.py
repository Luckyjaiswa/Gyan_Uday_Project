from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Students CRUD
    path('',                       views.student_list,    name='list'),
    path('create/',                views.student_create,  name='create'),
    path('<int:pk>/',              views.student_detail,  name='detail'),
    path('<int:pk>/edit/',         views.student_update,  name='update'),
    path('<int:pk>/delete/',       views.student_delete,  name='delete'),

    # Departments
    path('departments/',           views.department_list,   name='department_list'),
    path('departments/create/',    views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),

    # Faculty
    path('faculty/',               views.faculty_list,    name='faculty_list'),
]
