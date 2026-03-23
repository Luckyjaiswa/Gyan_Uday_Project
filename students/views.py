from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Student, Department, FacultyProfile
from .forms import StudentForm, DepartmentForm, FacultyProfileForm, StudentFilterForm


# ═══════════════════════════════════════════════════════════
# STUDENT VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def student_list(request):
    """
    Lists all students with search, filter, and pagination.
    Demonstrates: Q objects for OR search, filter chaining, Paginator.
    """
    form = StudentFilterForm(request.GET)
    # Use select_related to fetch department in same query (avoids N+1 queries)
    students = Student.objects.select_related('department').all()

    if form.is_valid():
        search = form.cleaned_data.get('search')
        department = form.cleaned_data.get('department')
        year   = form.cleaned_data.get('year')
        status = form.cleaned_data.get('status')

        if search:
            # Q objects allow OR filtering across multiple fields
            students = students.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)  |
                Q(roll_number__icontains=search) |
                Q(email__icontains=search)
            )
        if department:
            students = students.filter(department=department)
        if year:
            students = students.filter(year=year)
        if status:
            students = students.filter(status=status)

    # Pagination — 20 students per page
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title':  'Students',
        'students':    page_obj,
        'form':        form,
        'total_count': students.count(),
        'departments': Department.objects.annotate(count=Count('students')),
    }
    return render(request, 'students/list.html', context)


@login_required
def student_detail(request, pk):
    """
    Shows full profile of a single student.
    Demonstrates: get_object_or_404, related model access via reverse FK.
    """
    student = get_object_or_404(
        Student.objects.select_related('department', 'user'),
        pk=pk
    )
    attendance_pct = student.get_attendance_percentage()

    context = {
        'page_title': f'{student.get_full_name()} — Profile',
        'student':    student,
        'attendance_pct': attendance_pct,
    }
    return render(request, 'students/detail.html', context)


@login_required
def student_create(request):
    """
    Create a new student record.
    GET  → blank form
    POST → validate and save
    """
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.get_full_name()} enrolled successfully.')
            return redirect('students:detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()

    return render(request, 'students/form.html', {
        'page_title': 'Enroll New Student',
        'form': form,
        'action': 'Create',
    })


@login_required
def student_update(request, pk):
    """
    Edit an existing student record.
    instance= pre-populates the form with existing data.
    """
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.get_full_name()} updated successfully.')
            return redirect('students:detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/form.html', {
        'page_title': f'Edit — {student.get_full_name()}',
        'form': form,
        'student': student,
        'action': 'Update',
    })


@login_required
def student_delete(request, pk):
    """
    Delete a student after confirmation.
    Only handles POST (confirmation form) to prevent accidental GET deletions.
    """
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        name = student.get_full_name()
        student.delete()
        messages.success(request, f'Student {name} has been removed.')
        return redirect('students:list')

    return render(request, 'students/confirm_delete.html', {
        'page_title': 'Delete Student',
        'student': student,
    })


# ═══════════════════════════════════════════════════════════
# DEPARTMENT VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def department_list(request):
    """Lists all departments with student count using annotate."""
    departments = Department.objects.annotate(
        student_count=Count('students')
    ).select_related('hod')

    return render(request, 'students/department_list.html', {
        'page_title':  'Departments',
        'departments': departments,
    })


@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'Department "{dept.name}" created.')
            return redirect('students:department_list')
    else:
        form = DepartmentForm()

    return render(request, 'students/department_form.html', {
        'page_title': 'Add Department',
        'form': form,
        'action': 'Create',
    })


@login_required
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{dept.name}" updated.')
            return redirect('students:department_list')
    else:
        form = DepartmentForm(instance=dept)

    return render(request, 'students/department_form.html', {
        'page_title': f'Edit — {dept.name}',
        'form': form,
        'action': 'Update',
    })


# ═══════════════════════════════════════════════════════════
# FACULTY VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def faculty_list(request):
    """Lists all faculty members with their department."""
    faculty = FacultyProfile.objects.select_related('user', 'department').all()

    return render(request, 'students/faculty_list.html', {
        'page_title': 'Faculty',
        'faculty': faculty,
    })
