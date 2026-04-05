from django.contrib import admin
from .models import Exam, Mark, ActivityLog


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display  = ('name', 'course', 'exam_type', 'exam_date', 'total_marks', 'status')
    list_filter   = ('exam_type', 'status', 'course__department')
    search_fields = ('name', 'course__code')
    date_hierarchy = 'exam_date'


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display  = ('student', 'exam', 'marks_obtained', 'grade', 'is_absent', 'entered_by')
    list_filter   = ('grade', 'is_absent', 'exam__course__department')
    search_fields = ('student__roll_number', 'student__first_name')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display  = ('action', 'description', 'actor', 'created_at')
    list_filter   = ('action',)
    readonly_fields = ('action', 'description', 'actor', 'created_at')
    ordering      = ('-created_at',)
