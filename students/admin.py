from django.contrib import admin
from .models import Department, Student, FacultyProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'hod', 'student_count', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ('roll_number', 'get_full_name', 'department', 'year', 'semester', 'status')
    list_filter   = ('department', 'year', 'status', 'gender')
    search_fields = ('roll_number', 'first_name', 'last_name', 'email')
    ordering      = ('roll_number',)


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'employee_id', 'department', 'designation')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id')
