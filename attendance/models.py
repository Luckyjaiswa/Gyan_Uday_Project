from django.db import models
from django.db.models import Count, Case, When, FloatField, Value
from django.db.models.functions import Cast
from students.models import Student
from courses.models import Course


class Attendance(models.Model):
    """
    Records daily attendance for a student in a course.

    ORM concepts demonstrated here (Phase 4 focus):
    - annotate()     : add computed columns to querysets
    - aggregate()    : reduce a queryset to a single value
    - Count()        : count related records
    - Case/When      : conditional expressions (like SQL CASE WHEN)
    - F expressions  : reference field values in queries
    - values()       : return dicts instead of model instances
    - values_list()  : return tuples instead of model instances
    """

    STATUS_PRESENT = 'present'
    STATUS_ABSENT  = 'absent'
    STATUS_LATE    = 'late'
    STATUS_EXCUSED = 'excused'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT,  'Absent'),
        (STATUS_LATE,    'Late'),
        (STATUS_EXCUSED, 'Excused'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    course  = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date    = models.DateField()
    status  = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PRESENT,
    )
    remarks = models.CharField(max_length=200, blank=True, null=True)
    marked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='attendance_marked',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'date')
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.roll_number} | {self.course.code} | {self.date} | {self.status}"

    # ─────────────────────────────────────────────────────────
    # CLASS METHODS — ORM aggregation examples (Phase 4)
    # ─────────────────────────────────────────────────────────

    @classmethod
    def get_student_percentage(cls, student, course=None):
        """
        Returns attendance percentage for a student.
        Optionally filtered to a specific course.

        ORM used: aggregate() + Count() + Case/When
        """
        qs = cls.objects.filter(student=student)
        if course:
            qs = qs.filter(course=course)

        result = qs.aggregate(
            total=Count('id'),
            present=Count(
                Case(
                    When(status__in=[cls.STATUS_PRESENT, cls.STATUS_LATE], then=1),
                    output_field=FloatField(),
                )
            )
        )
        total = result['total']
        if total == 0:
            return None
        return round((result['present'] / total) * 100, 1)

    @classmethod
    def get_course_summary(cls, course):
        """
        Returns per-student attendance summary for a course.

        ORM used: values() + annotate() + Count() + Case/When
        This is a single optimised DB query instead of looping.
        """
        return (
            cls.objects
            .filter(course=course)
            .values('student__id', 'student__first_name',
                    'student__last_name', 'student__roll_number')
            .annotate(
                total=Count('id'),
                present=Count(Case(
                    When(status__in=[cls.STATUS_PRESENT, cls.STATUS_LATE], then=1),
                    output_field=FloatField(),
                )),
                absent=Count(Case(
                    When(status=cls.STATUS_ABSENT, then=1),
                    output_field=FloatField(),
                )),
            )
            .order_by('student__roll_number')
        )

    @classmethod
    def get_department_averages(cls):
        """
        Returns average attendance % grouped by department.
        Used in the dashboard chart.

        ORM used: values() → annotate() → aggregate across FK chain
        """
        return (
            cls.objects
            .values('student__department__name')
            .annotate(
                total=Count('id'),
                present=Count(Case(
                    When(status__in=[cls.STATUS_PRESENT, cls.STATUS_LATE], then=1),
                    output_field=FloatField(),
                )),
            )
            .order_by('student__department__name')
        )
