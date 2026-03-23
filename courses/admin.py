from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'department', 'faculty', 'semester', 'course_type', 'credits', 'is_active')
    list_filter   = ('department', 'semester', 'course_type', 'is_active')
    search_fields = ('code', 'name')
    ordering      = ('code',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'enrolled_on', 'is_active', 'grade')
    list_filter   = ('course__department', 'is_active')
    search_fields = ('student__roll_number', 'student__first_name', 'course__code')
