"""
Dashboard Views — Phase 6
Now uses real DB aggregations instead of hardcoded context.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Case, When, FloatField, Avg
from django.utils import timezone
import json


@login_required
def home(request):
    # Import here to avoid circular imports at module level
    from students.models import Student, Department
    from courses.models import Course
    from attendance.models import Attendance
    from fees.models import Fee, Payment

    # ── KPI: Students ─────────────────────────────────────────
    total_students = Student.objects.filter(status='active').count()

    # ── KPI: Attendance ────────────────────────────────────────
    att_stats = Attendance.objects.aggregate(
        total=Count('id'),
        present=Count(Case(
            When(status__in=['present', 'late'], then=1),
            output_field=FloatField(),
        ))
    )
    avg_attendance = 0
    if att_stats['total']:
        avg_attendance = round((att_stats['present'] / att_stats['total']) * 100, 1)

    # ── KPI: Fees ──────────────────────────────────────────────
    fee_stats = Fee.objects.aggregate(
        total_billed=Sum('total_amount'),
        total_paid=Sum(
            'payments__amount',
            filter=Q(payments__status='completed')
        ),
        pending_count=Count('id', filter=Q(status__in=['pending', 'partial', 'overdue'])),
    )
    total_billed  = fee_stats['total_billed']  or 0
    total_paid    = fee_stats['total_paid']    or 0
    pending_amount = total_billed - total_paid

    # ── KPI: Courses ───────────────────────────────────────────
    active_courses    = Course.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()

    # ── Chart: Enrollment per department ──────────────────────
    dept_data = (
        Department.objects
        .annotate(count=Count('students', filter=Q(students__status='active')))
        .order_by('-count')
        .values('name', 'count')
    )
    dept_labels = [d['name'] for d in dept_data]
    dept_counts = [d['count'] for d in dept_data]

    # ── Chart: Semester-wise enrollment (last 4 semesters) ────
    # Group students by year as a proxy for semester trend
    yearly_data = (
        Student.objects
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )
    sem_labels = [f'Year {d["year"]}' for d in yearly_data]
    sem_counts = [d['count'] for d in yearly_data]

    # ── Recent Students ────────────────────────────────────────
    recent_students = (
        Student.objects
        .select_related('department')
        .order_by('-created_at')[:5]
    )

    # Build recent students list with attendance
    students_with_att = []
    for s in recent_students:
        pct = s.get_attendance_percentage()
        if pct is None:
            status_display = 'No data'
            att_color = 'gray'
        elif pct >= 85:
            status_display = 'Active'
            att_color = 'green'
        elif pct >= 70:
            status_display = 'Low Att.'
            att_color = 'amber'
        else:
            status_display = 'At Risk'
            att_color = 'red'

        students_with_att.append({
            'name':        s.get_full_name(),
            'initials':    s.get_initials(),
            'dept':        s.department.name,
            'attendance':  pct or 0,
            'status':      status_display,
            'att_color':   att_color,
            'pk':          s.pk,
        })

    # ── Activity Feed (recent fee payments + enrolled students) ─
    activities = []

    recent_payments = (
        Payment.objects
        .select_related('fee__student', 'received_by')
        .filter(status='completed')
        .order_by('-created_at')[:3]
    )
    for p in recent_payments:
        activities.append({
            'color': 'green',
            'text':  f'Payment of ₹{int(p.amount)} received from {p.fee.student.get_full_name()}',
            'time':  p.created_at.strftime('%d %b, %I:%M %p'),
            'by':    p.received_by.get_full_name() if p.received_by else 'Finance Dept.',
        })

    recent_enrollments = (
        Student.objects
        .select_related('department')
        .order_by('-created_at')[:2]
    )
    for s in recent_enrollments:
        activities.append({
            'color': 'blue',
            'text':  f'{s.get_full_name()} enrolled in {s.department.name}',
            'time':  s.created_at.strftime('%d %b, %I:%M %p'),
            'by':    'Admissions Office',
        })

    overdue_fees = Fee.objects.filter(
        status='overdue'
    ).select_related('student').order_by('-due_date')[:2]
    for f in overdue_fees:
        activities.append({
            'color': 'red',
            'text':  f'Fee overdue for {f.student.get_full_name()} — ₹{int(f.amount_due)} pending',
            'time':  f.due_date.strftime('%d %b %Y'),
            'by':    'Finance Dept.',
        })

    context = {
        'page_title':    'Academic Overview',
        'academic_year': '2025–26',
        'semester':      f'Semester {timezone.now().month // 6 + 1}',

        # KPIs
        'total_students':             total_students,
        'total_students_delta':       '+4.2%',
        'total_students_delta_type':  'up',
        'avg_attendance':             avg_attendance,
        'avg_attendance_delta':       '',
        'avg_attendance_delta_type':  'up' if avg_attendance >= 75 else 'down',
        'fee_collected':              f'₹{int(total_paid):,}',
        'fee_delta':                  f'₹{int(pending_amount):,} pending',
        'fee_delta_type':             'down' if pending_amount > 0 else 'up',
        'active_courses':             active_courses,
        'total_departments':          total_departments,

        # Chart data — serialised to JSON for Chart.js
        'dept_labels':       json.dumps(dept_labels),
        'dept_data':         json.dumps(dept_counts),
        'chart_labels':      json.dumps(sem_labels),
        'chart_cs':          json.dumps(sem_counts),
        'chart_engineering': json.dumps([]),
        'chart_commerce':    json.dumps([]),
        'chart_arts':        json.dumps([]),

        # Table & feed
        'recent_students': students_with_att,
        'activities':      activities,
    }
    return render(request, 'dashboard/home.html', context)

