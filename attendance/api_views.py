"""
attendance/api_views.py — Phase 5
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, FloatField

from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceSummarySerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    /api/attendance/
    /api/attendance/<id>/
    /api/attendance/summary/          ← aggregated stats for dashboard
    /api/attendance/department-stats/ ← per-department averages for chart
    """
    queryset = Attendance.objects.select_related(
        'student', 'course', 'course__department', 'marked_by'
    ).order_by('-date')

    serializer_class   = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['student', 'course', 'date', 'status']
    ordering_fields    = ['date', 'student__roll_number']

    def perform_create(self, serializer):
        """
        Automatically set marked_by to the currently logged-in user.
        perform_create() is called by CreateModelMixin after validation.
        """
        serializer.save(marked_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        GET /api/attendance/summary/?course=<id>
        Returns per-student attendance summary for a course.
        Uses the ORM class method we built in Phase 4.
        """
        from courses.models import Course
        course_id = request.query_params.get('course')
        if not course_id:
            return Response(
                {'error': 'course query param is required. e.g. ?course=1'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=404)

        raw = Attendance.get_course_summary(course)
        rows = []
        for row in raw:
            pct = round((row['present'] / row['total']) * 100, 1) if row['total'] else 0
            rows.append({
                'student_id':   row['student__id'],
                'student_name': f"{row['student__first_name']} {row['student__last_name']}",
                'roll_number':  row['student__roll_number'],
                'total':        row['total'],
                'present':      row['present'],
                'absent':       row['absent'],
                'percentage':   pct,
            })
        return Response({
            'course_code': course.code,
            'course_name': course.name,
            'count':       len(rows),
            'students':    rows,
        })

    @action(detail=False, methods=['get'], url_path='department-stats')
    def department_stats(self, request):
        """
        GET /api/attendance/department-stats/
        Used by the dashboard Chart.js chart to show per-department averages.
        """
        raw = Attendance.get_department_averages()
        results = []
        for row in raw:
            pct = round((row['present'] / row['total']) * 100, 1) if row['total'] else 0
            results.append({
                'department': row['student__department__name'],
                'total':      row['total'],
                'present':    row['present'],
                'percentage': pct,
            })
        return Response(results)
