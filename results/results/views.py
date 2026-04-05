from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Max, Min

from .models import Exam, Mark, ActivityLog
from .forms import ExamForm, MarkForm, BulkMarkEntryForm
from students.models import Student
from courses.models import Course, Enrollment


# ═══════════════════════════════════════════════════════════
# EXAM VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def exam_list(request):
    """Lists all exams with stats — annotate adds avg marks in one query."""
    exams = (
        Exam.objects
        .select_related('course', 'course__department')
        .annotate(
            marks_count=Count('marks'),
            avg_marks=Avg('marks__marks_obtained'),
        )
        .order_by('-exam_date')
    )
    return render(request, 'results/exam_list.html', {
        'page_title': 'Examinations',
        'exams':      exams,
    })


@login_required
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.name}" scheduled for {exam.exam_date}.')
            return redirect('results:exam_detail', pk=exam.pk)
    else:
        form = ExamForm()
    return render(request, 'results/exam_form.html', {
        'page_title': 'Schedule Exam',
        'form': form,
        'action': 'Schedule',
    })


@login_required
def exam_detail(request, pk):
    """Shows exam details and all marks entered for it."""
    exam  = get_object_or_404(Exam.objects.select_related('course', 'course__department'), pk=pk)
    marks = (
        exam.marks
        .select_related('student', 'student__department')
        .order_by('-marks_obtained')
    )
    # Grade distribution using values() + annotate()
    grade_dist = (
        exam.marks
        .values('grade')
        .annotate(count=Count('id'))
        .order_by('grade')
    )
    return render(request, 'results/exam_detail.html', {
        'page_title': exam.name,
        'exam':       exam,
        'marks':      marks,
        'grade_dist': grade_dist,
        'pass_count': exam.get_pass_count(),
        'fail_count': exam.get_fail_count(),
        'avg_marks':  exam.get_average_marks(),
    })


# ═══════════════════════════════════════════════════════════
# MARK ENTRY VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def bulk_mark_entry(request, exam_pk):
    """
    Enter marks for all enrolled students in one exam at once.
    POST saves all marks using bulk_create / individual saves.
    Signals fire automatically for each Mark saved.
    """
    exam = get_object_or_404(Exam, pk=exam_pk)

    # Get enrolled students for this course
    enrollments = (
        Enrollment.objects
        .filter(course=exam.course, is_active=True)
        .select_related('student')
        .order_by('student__roll_number')
    )

    # Existing marks map: student_id → Mark instance
    existing_marks = {
        m.student_id: m
        for m in Mark.objects.filter(exam=exam)
    }

    if request.method == 'POST':
        saved = 0
        for enr in enrollments:
            student   = enr.student
            raw_marks = request.POST.get(f'marks_{student.pk}', '').strip()
            is_absent = request.POST.get(f'absent_{student.pk}') == 'on'
            remarks   = request.POST.get(f'remarks_{student.pk}', '').strip()

            if not raw_marks and not is_absent:
                continue  # skip blank entries

            try:
                marks_val = float(raw_marks) if raw_marks else 0
                if not is_absent and marks_val > exam.total_marks:
                    messages.error(
                        request,
                        f'{student.get_full_name()}: marks cannot exceed {exam.total_marks}.'
                    )
                    continue

                if student.pk in existing_marks:
                    # Update existing
                    m = existing_marks[student.pk]
                    m.marks_obtained = marks_val
                    m.is_absent      = is_absent
                    m.remarks        = remarks
                    m.entered_by     = request.user
                    m.save()
                else:
                    # Create new — signal fires automatically
                    Mark.objects.create(
                        student        = student,
                        exam           = exam,
                        marks_obtained = marks_val,
                        is_absent      = is_absent,
                        remarks        = remarks,
                        entered_by     = request.user,
                    )
                saved += 1
            except (ValueError, TypeError):
                messages.error(request, f'Invalid marks for {student.get_full_name()}.')

        if saved:
            messages.success(request, f'Marks saved for {saved} student(s).')
        return redirect('results:exam_detail', pk=exam.pk)

    return render(request, 'results/bulk_mark_entry.html', {
        'page_title':     f'Enter Marks — {exam.name}',
        'exam':           exam,
        'enrollments':    enrollments,
        'existing_marks': existing_marks,
    })


# ═══════════════════════════════════════════════════════════
# STUDENT RESULT CARD
# ═══════════════════════════════════════════════════════════

@login_required
def student_result_card(request, student_pk):
    """
    Shows all results for a student across all exams.
    Demonstrates: prefetch_related for reverse FK,
    aggregate for overall stats.
    """
    student = get_object_or_404(Student.objects.select_related('department'), pk=student_pk)
    marks   = (
        Mark.objects
        .filter(student=student)
        .select_related('exam', 'exam__course', 'exam__course__department')
        .order_by('-exam__exam_date')
    )

    # Aggregate stats
    stats = marks.filter(is_absent=False).aggregate(
        avg_pct  = Avg('marks_obtained'),
        total    = Count('id'),
        highest  = Max('marks_obtained'),
        lowest   = Min('marks_obtained'),
    )

    # Grade distribution
    grade_dist = (
        marks.values('grade')
        .annotate(count=Count('id'))
        .order_by('grade')
    )

    return render(request, 'results/student_result_card.html', {
        'page_title': f'Result Card — {student.get_full_name()}',
        'student':    student,
        'marks':      marks,
        'stats':      stats,
        'grade_dist': grade_dist,
    })


# ═══════════════════════════════════════════════════════════
# ACTIVITY LOG
# ═══════════════════════════════════════════════════════════

@login_required
def activity_log(request):
    """Shows the live activity feed powered by signals."""
    logs = ActivityLog.objects.select_related('actor').order_by('-created_at')[:100]
    return render(request, 'results/activity_log.html', {
        'page_title': 'Activity Log',
        'logs':       logs,
    })


# Alias for marks list (used in base.html nav)
@login_required
def marks_list(request):
    return redirect('results:exam_list')
