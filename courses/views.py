from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import Course, Enrollment
from .forms import CourseForm, EnrollmentForm
from students.models import Student, Department


@login_required
def course_list(request):
    """
    Lists all courses.
    Demonstrates: select_related to avoid N+1 queries,
    annotate to add enrolled_count without extra queries.
    """
    courses = (
        Course.objects
        .select_related('department', 'faculty')
        .annotate(enrolled_count=Count('enrollments'))
        .filter(is_active=True)
        .order_by('department', 'semester', 'code')
    )

    # Group by department for display
    departments = Department.objects.prefetch_related(
        'courses'
    ).filter(courses__is_active=True).distinct()

    return render(request, 'courses/list.html', {
        'page_title': 'Courses',
        'courses':    courses,
        'departments': departments,
        'total_count': courses.count(),
    })


@login_required
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.select_related('department', 'faculty'),
        pk=pk
    )
    # Get all active enrollments for this course using select_related
    enrollments = (
        Enrollment.objects
        .filter(course=course, is_active=True)
        .select_related('student', 'student__department')
        .order_by('student__roll_number')
    )
    return render(request, 'courses/detail.html', {
        'page_title': course.name,
        'course': course,
        'enrollments': enrollments,
    })


@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.name}" created successfully.')
            return redirect('courses:detail', pk=course.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()

    return render(request, 'courses/form.html', {
        'page_title': 'Add New Course',
        'form': form,
        'action': 'Create',
    })


@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.name}" updated.')
            return redirect('courses:detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/form.html', {
        'page_title': f'Edit — {course.name}',
        'form': form,
        'action': 'Update',
        'course': course,
    })


@login_required
def enrollment_create(request, course_pk):
    """Enroll a student into a course."""
    course = get_object_or_404(Course, pk=course_pk)

    # Exclude already-enrolled students from the dropdown
    already_enrolled = Enrollment.objects.filter(
        course=course
    ).values_list('student_id', flat=True)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.course = course
            enrollment.save()
            messages.success(
                request,
                f'{enrollment.student.get_full_name()} enrolled in {course.code}.'
            )
            return redirect('courses:detail', pk=course.pk)
    else:
        form = EnrollmentForm(initial={'course': course})
        # Limit student choices to those not already enrolled
        form.fields['student'].queryset = Student.objects.exclude(
            id__in=already_enrolled
        )
        form.fields['course'].widget = form.fields['course'].hidden_widget()

    return render(request, 'courses/enrollment_form.html', {
        'page_title': f'Enroll Student — {course.code}',
        'form': form,
        'course': course,
    })
