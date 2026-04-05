"""
students/api_views.py — Phase 5

DRF ViewSets — Key concepts:
- ModelViewSet      : provides list, create, retrieve, update, destroy automatically
- ReadOnlyModelViewSet : only list + retrieve (no write operations)
- @action decorator : adds custom endpoints beyond CRUD (e.g. /students/1/attendance/)
- get_serializer_class : return different serializers for list vs detail
- get_queryset      : dynamically filter based on request/query params
- permission_classes: control who can access what
- IsAuthenticated   : requires valid session or JWT token
- IsAdminUser       : only staff/superusers
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Student, Department, FacultyProfile
from .serializers import (
    StudentListSerializer, StudentDetailSerializer,
    DepartmentSerializer, FacultyProfileSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    /api/departments/
    /api/departments/<id>/

    Full CRUD for departments.
    Only admins can create/update/delete.
    Anyone authenticated can list/retrieve.
    """
    queryset         = Department.objects.annotate(
        student_count=Count('students')
    ).order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['name', 'code']

    def get_permissions(self):
        """
        Override to apply different permissions per action.
        list/retrieve → IsAuthenticated
        create/update/destroy → IsAdminUser
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [IsAuthenticated()]


class StudentViewSet(viewsets.ModelViewSet):
    """
    /api/students/              → list all students (GET) / create (POST)
    /api/students/<id>/         → retrieve (GET) / update (PUT/PATCH) / delete (DELETE)
    /api/students/<id>/attendance_report/  → custom action: student's attendance
    /api/students/at_risk/      → custom action: students below 75% attendance

    Key teaching points:
    - get_serializer_class()  : list uses lightweight serializer, detail uses full one
    - get_queryset()          : filter by query params (?department=1&year=2)
    - @action                 : adds extra endpoints outside standard CRUD
    """
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['department', 'year', 'semester', 'status', 'gender']
    search_fields      = ['first_name', 'last_name', 'roll_number', 'email']
    ordering_fields    = ['roll_number', 'first_name', 'created_at']
    ordering           = ['roll_number']

    def get_queryset(self):
        """
        Returns filtered queryset based on query parameters.
        Always use select_related to avoid N+1 queries.
        """
        return Student.objects.select_related('department').all()

    def get_serializer_class(self):
        """
        Use lightweight serializer for list, full serializer for everything else.
        This keeps list responses fast and detail responses complete.
        """
        if self.action == 'list':
            return StudentListSerializer
        return StudentDetailSerializer

    # ── Custom Actions ─────────────────────────────────────────

    @action(detail=True, methods=['get'], url_path='attendance-report')
    def attendance_report(self, request, pk=None):
        """
        GET /api/students/<id>/attendance-report/
        Returns per-course attendance breakdown for one student.
        @action(detail=True) means this applies to a single object.
        """
        from attendance.models import Attendance
        from django.db.models import Case, When, FloatField

        student = self.get_object()
        course_stats = (
            Attendance.objects
            .filter(student=student)
            .values('course__id', 'course__code', 'course__name')
            .annotate(
                total=Count('id'),
                present=Count(Case(
                    When(status__in=['present', 'late'], then=1),
                    output_field=FloatField(),
                )),
                absent=Count(Case(
                    When(status='absent', then=1),
                    output_field=FloatField(),
                )),
            )
        )
        rows = []
        for row in course_stats:
            pct = round((row['present'] / row['total']) * 100, 1) if row['total'] else 0
            rows.append({
                'course_id':   row['course__id'],
                'course_code': row['course__code'],
                'course_name': row['course__name'],
                'total':       row['total'],
                'present':     row['present'],
                'absent':      row['absent'],
                'percentage':  pct,
            })
        overall = Attendance.get_student_percentage(student)
        return Response({
            'student_id':   student.pk,
            'student_name': student.get_full_name(),
            'roll_number':  student.roll_number,
            'overall_percentage': overall,
            'courses': rows,
        })

    @action(detail=False, methods=['get'], url_path='at-risk')
    def at_risk(self, request):
        """
        GET /api/students/at-risk/
        Returns students whose overall attendance is below 75%.
        @action(detail=False) means this is a list-level endpoint (no pk).
        """
        from attendance.models import Attendance
        from django.db.models import Case, When, FloatField

        students = Student.objects.select_related('department').filter(status='active')
        at_risk_list = []

        for student in students:
            pct = Attendance.get_student_percentage(student)
            if pct is not None and pct < 75:
                at_risk_list.append({
                    'id':          student.pk,
                    'roll_number': student.roll_number,
                    'full_name':   student.get_full_name(),
                    'department':  student.department.name,
                    'attendance_percentage': pct,
                })

        at_risk_list.sort(key=lambda x: x['attendance_percentage'])
        return Response({
            'count':    len(at_risk_list),
            'students': at_risk_list,
        })


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/faculty/       → list all faculty (read-only)
    /api/faculty/<id>/  → retrieve one faculty member

    ReadOnlyModelViewSet provides only list + retrieve.
    No create/update/delete exposed via API.
    """
    queryset = FacultyProfile.objects.select_related(
        'user', 'department'
    ).all()
    serializer_class   = FacultyProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['department']
    search_fields      = ['user__first_name', 'user__last_name', 'employee_id']
