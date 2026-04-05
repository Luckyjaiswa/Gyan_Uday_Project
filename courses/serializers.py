"""
courses/serializers.py — Phase 5
"""

from rest_framework import serializers
from .models import Course, Enrollment
from students.serializers import StudentListSerializer


class CourseSerializer(serializers.ModelSerializer):
    department_name  = serializers.CharField(source='department.name', read_only=True)
    faculty_name     = serializers.CharField(source='faculty.get_full_name', read_only=True)
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    enrolled_count   = serializers.SerializerMethodField()

    class Meta:
        model  = Course
        fields = (
            'id', 'code', 'name', 'description',
            'department', 'department_name',
            'faculty', 'faculty_name',
            'credits', 'semester', 'course_type', 'course_type_display',
            'is_active', 'enrolled_count', 'created_at',
        )
        read_only_fields = ('created_at',)

    def get_enrolled_count(self, obj):
        return obj.enrollments.filter(is_active=True).count()


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name    = serializers.CharField(source='student.get_full_name', read_only=True)
    student_roll    = serializers.CharField(source='student.roll_number', read_only=True)
    course_code     = serializers.CharField(source='course.code', read_only=True)
    course_name     = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model  = Enrollment
        fields = (
            'id', 'student', 'student_name', 'student_roll',
            'course', 'course_code', 'course_name',
            'enrolled_on', 'is_active', 'grade',
        )
        read_only_fields = ('enrolled_on',)

    def validate(self, data):
        """Prevent duplicate enrollments."""
        student = data.get('student')
        course  = data.get('course')
        if student and course:
            qs = Enrollment.objects.filter(student=student, course=course)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"{student.get_full_name()} is already enrolled in {course.code}."
                )
        return data
