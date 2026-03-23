from django.db import models
from students.models import Department, Student
from accounts.models import User


class Course(models.Model):
    """
    Represents an academic course offered by a department.

    ORM concepts demonstrated:
    - ForeignKey to Department (many courses → one department)
    - ForeignKey to User/faculty (many courses → one faculty)
    - ManyToManyField via Enrollment (students ↔ courses)
    """

    COURSE_TYPE_THEORY    = 'theory'
    COURSE_TYPE_LAB       = 'lab'
    COURSE_TYPE_PROJECT   = 'project'
    COURSE_TYPE_ELECTIVE  = 'elective'

    COURSE_TYPE_CHOICES = [
        (COURSE_TYPE_THEORY,   'Theory'),
        (COURSE_TYPE_LAB,      'Lab'),
        (COURSE_TYPE_PROJECT,  'Project'),
        (COURSE_TYPE_ELECTIVE, 'Elective'),
    ]

    SEM_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]

    code        = models.CharField(max_length=20, unique=True)   # e.g. CS401
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    department  = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='courses',
    )
    faculty     = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'faculty'},
        related_name='courses_taught',
    )
    credits     = models.PositiveIntegerField(default=3)
    semester    = models.IntegerField(choices=SEM_CHOICES, default=1)
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        default=COURSE_TYPE_THEORY,
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def enrolled_count(self):
        return self.enrollments.filter(is_active=True).count()

    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        ordering = ['code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class Enrollment(models.Model):
    """
    Junction table linking Students to Courses.
    This is the explicit through-model for a ManyToMany relationship.

    Teaching point: Django auto-creates a hidden junction table for
    ManyToManyField, but using an explicit through model lets you
    add extra fields (grade, is_active, enrolled_on).
    """
    student     = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    course      = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    enrolled_on = models.DateField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)
    grade       = models.CharField(max_length=5, blank=True, null=True)  # e.g. A+, B, C

    class Meta:
        unique_together = ('student', 'course')   # prevent duplicate enrollments
        ordering = ['-enrolled_on']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'

    def __str__(self):
        return f"{self.student.roll_number} → {self.course.code}"
