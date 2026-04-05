"""
attendance/serializers.py — Phase 5
"""

from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student_name   = serializers.CharField(source='student.get_full_name', read_only=True)
    student_roll   = serializers.CharField(source='student.roll_number',  read_only=True)
    course_code    = serializers.CharField(source='course.code',          read_only=True)
    status_display = serializers.CharField(source='get_status_display',   read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)

    class Meta:
        model  = Attendance
        fields = (
            'id', 'student', 'student_name', 'student_roll',
            'course', 'course_code',
            'date', 'status', 'status_display',
            'remarks', 'marked_by', 'marked_by_name', 'created_at',
        )
        read_only_fields = ('created_at', 'marked_by')

    def validate(self, data):
        """Prevent duplicate attendance for same student+course+date."""
        student = data.get('student')
        course  = data.get('course')
        date    = data.get('date')
        if student and course and date:
            qs = Attendance.objects.filter(student=student, course=course, date=date)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Attendance already marked for this student on this date in this course."
                )
        return data


class AttendanceSummarySerializer(serializers.Serializer):
    """
    Read-only serializer for aggregated attendance data.
    Used by the dashboard chart API endpoint.
    Not backed by a model — uses Serializer (not ModelSerializer).
    """
    student_id   = serializers.IntegerField()
    student_name = serializers.CharField()
    roll_number  = serializers.CharField()
    total        = serializers.IntegerField()
    present      = serializers.IntegerField()
    absent       = serializers.IntegerField()
    percentage   = serializers.FloatField()
