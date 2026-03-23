from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Case, When, FloatField, Q
from django.utils import timezone

from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm, AttendanceFilterForm
from students.models import Student
from courses.models import Course, Enrollment


# ═══════════════════════════════════════════════════════════
# ATTENDANCE LIST — with filters
# ═══════════════════════════════════════════════════════════

@login_required
def attendance_list(request):
    """
    Shows all attendance records with filter support.
    Demonstrates: chained filter(), select_related(), Q objects.
    """
    form = AttendanceFilterForm(request.GET)
    records = (
        Attendance.objects
        .select_related('student', 'course', 'course__department')
        .order_by('-date')
    )

    if form.is_valid():
        course    = form.cleaned_data.get('course')
        student   = form.cleaned_data.get('student')
        date_from = form.cleaned_data.get('date_from')
        date_to   = form.cleaned_data.get('date_to')

        if course:
            records = records.filter(course=course)
        if student:
            records = records.filter(student=student)
        if date_from:
            records = records.filter(date__gte=date_from)
        if date_to:
            records = records.filter(date__lte=date_to)

    return render(request, 'attendance/list.html', {
        'page_title': 'Attendance Records',
        'records':    records[:200],   # cap display at 200 rows
        'form':       form,
        'total':      records.count(),
    })


# ═══════════════════════════════════════════════════════════
# BULK MARK ATTENDANCE — for a whole class on a date
# ═══════════════════════════════════════════════════════════

@login_required
def bulk_mark(request):
    """
    Step 1 (GET with course+date) → show all enrolled students.
    Step 2 (POST) → save attendance for each student.

    Key ORM: bulk_create() saves all records in ONE query
    instead of N individual INSERT statements.
    """
    students_to_mark = []
    course = None
    date   = None

    if request.method == 'GET' and request.GET.get('course') and request.GET.get('date'):
        course_id = request.GET.get('course')
        date      = request.GET.get('date')
        try:
            course = Course.objects.get(pk=course_id)
            # Get all active enrolled students for this course
            enrollments = Enrollment.objects.filter(
                course=course, is_active=True
            ).select_related('student').order_by('student__roll_number')
            students_to_mark = enrollments

            # Pre-fill with existing records for this date (if re-marking)
            existing = Attendance.objects.filter(
                course=course, date=date
            ).values('student_id', 'status')
            existing_map = {e['student_id']: e['status'] for e in existing}

        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')

    elif request.method == 'POST':
        course_id = request.POST.get('course_id')
        date      = request.POST.get('date')
        course    = get_object_or_404(Course, pk=course_id)

        # Collect statuses from POST data
        student_ids = request.POST.getlist('student_ids')
        records_to_create = []
        records_to_update = []

        existing = Attendance.objects.filter(
            course=course, date=date
        ).values('student_id', 'id')
        existing_map = {e['student_id']: e['id'] for e in existing}

        for sid in student_ids:
            status = request.POST.get(f'status_{sid}', Attendance.STATUS_ABSENT)
            sid_int = int(sid)
            if sid_int in existing_map:
                # Update existing record
                Attendance.objects.filter(id=existing_map[sid_int]).update(
                    status=status,
                    marked_by=request.user,
                )
            else:
                records_to_create.append(
                    Attendance(
                        student_id=sid_int,
                        course=course,
                        date=date,
                        status=status,
                        marked_by=request.user,
                    )
                )

        # bulk_create inserts all new records in a SINGLE SQL query
        if records_to_create:
            Attendance.objects.bulk_create(records_to_create)

        messages.success(
            request,
            f'Attendance marked for {len(student_ids)} students in {course.code} on {date}.'
        )
        return redirect('attendance:list')

    form = BulkAttendanceForm(request.GET or None)

    return render(request, 'attendance/bulk_mark.html', {
        'page_title':       'Mark Attendance',
        'form':             form,
        'course':           course,
        'date':             date,
        'students_to_mark': students_to_mark,
        'existing_map':     existing_map if students_to_mark else {},
        'status_choices':   Attendance.STATUS_CHOICES,
    })


# ═══════════════════════════════════════════════════════════
# STUDENT ATTENDANCE REPORT
# ═══════════════════════════════════════════════════════════

@login_required
def student_report(request, student_pk):
    """
    Shows a per-course attendance breakdown for one student.

    ORM demonstrated:
    - annotate() to add total/present counts per course in ONE query
    - Case/When for conditional counting
    - Python-level percentage calculation from annotated values
    """
    student = get_object_or_404(Student, pk=student_pk)

    # Single query: for each course this student has records in,
    # count total and present records using annotate + Case/When
    course_stats = (
        Attendance.objects
        .filter(student=student)
        .values('course__id', 'course__code', 'course__name')
        .annotate(
            total=Count('id'),
            present=Count(Case(
                When(status__in=[Attendance.STATUS_PRESENT, Attendance.STATUS_LATE], then=1),
                output_field=FloatField(),
            )),
            absent=Count(Case(
                When(status=Attendance.STATUS_ABSENT, then=1),
                output_field=FloatField(),
            )),
        )
        .order_by('course__code')
    )

    # Add percentage in Python (can't do division directly in ORM annotation easily)
    stats_with_pct = []
    for row in course_stats:
        pct = round((row['present'] / row['total']) * 100, 1) if row['total'] else 0
        stats_with_pct.append({**row, 'percentage': pct})

    # Overall percentage across all courses
    overall = Attendance.get_student_percentage(student)

    return render(request, 'attendance/student_report.html', {
        'page_title':   f'Attendance Report — {student.get_full_name()}',
        'student':      student,
        'course_stats': stats_with_pct,
        'overall':      overall,
    })


# ═══════════════════════════════════════════════════════════
# COURSE ATTENDANCE SUMMARY
# ═══════════════════════════════════════════════════════════

@login_required
def course_summary(request, course_pk):
    """
    Shows per-student attendance summary for one course.
    Uses the class method on Attendance which runs a single
    annotated query for all students at once.
    """
    course = get_object_or_404(Course, pk=course_pk)
    summary = Attendance.get_course_summary(course)

    # Add percentages
    rows = []
    for row in summary:
        pct = round((row['present'] / row['total']) * 100, 1) if row['total'] else 0
        rows.append({**row, 'percentage': pct})

    return render(request, 'attendance/course_summary.html', {
        'page_title': f'Attendance Summary — {course.code}',
        'course':     course,
        'rows':       rows,
    })
