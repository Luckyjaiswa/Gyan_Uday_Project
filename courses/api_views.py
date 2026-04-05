"""
courses/api_views.py — Phase 5
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    /api/courses/
    /api/courses/<id>/
    /api/courses/<id>/enrolled_students/   ← custom action
    """
    queryset = Course.objects.select_related(
        'department', 'faculty'
    ).annotate(
        enrolled_count=Count('enrollments')
    ).filter(is_active=True)

    serializer_class   = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['department', 'semester', 'course_type', 'faculty']
    search_fields      = ['code', 'name']
    ordering_fields    = ['code', 'semester', 'credits']
    ordering           = ['code']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'], url_path='enrolled-students')
    def enrolled_students(self, request, pk=None):
        """
        GET /api/courses/<id>/enrolled-students/
        Returns all students enrolled in this course.
        """
        from students.serializers import StudentListSerializer
        course = self.get_object()
        enrolled = [
            enr.student for enr in
            Enrollment.objects.filter(course=course, is_active=True)
            .select_related('student', 'student__department')
        ]
        serializer = StudentListSerializer(enrolled, many=True)
        return Response({
            'course_code': course.code,
            'course_name': course.name,
            'count':       len(enrolled),
            'students':    serializer.data,
        })


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    /api/enrollments/
    /api/enrollments/<id>/
    """
    queryset = Enrollment.objects.select_related(
        'student', 'course', 'student__department'
    ).all()
    serializer_class   = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['student', 'course', 'is_active']
