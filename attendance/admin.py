from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'date', 'status', 'marked_by')
    list_filter   = ('status', 'course__department', 'date')
    search_fields = ('student__roll_number', 'student__first_name', 'course__code')
    date_hierarchy = 'date'
    ordering      = ('-date',)
