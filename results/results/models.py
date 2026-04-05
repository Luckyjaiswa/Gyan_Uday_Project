from django.db import models
from django.db.models import Sum, Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Student
from courses.models import Course


class Exam(models.Model):
    """
    Represents an examination event (e.g. Mid-Sem, End-Sem).
    """
    EXAM_TYPE_MIDSEM  = 'midsem'
    EXAM_TYPE_ENDSEM  = 'endsem'
    EXAM_TYPE_UNIT    = 'unit'
    EXAM_TYPE_PRACTICAL = 'practical'
    EXAM_TYPE_INTERNAL  = 'internal'

    EXAM_TYPE_CHOICES = [
        (EXAM_TYPE_MIDSEM,    'Mid-Semester'),
        (EXAM_TYPE_ENDSEM,    'End-Semester'),
        (EXAM_TYPE_UNIT,      'Unit Test'),
        (EXAM_TYPE_PRACTICAL, 'Practical'),
        (EXAM_TYPE_INTERNAL,  'Internal Assessment'),
    ]

    STATUS_UPCOMING   = 'upcoming'
    STATUS_ONGOING    = 'ongoing'
    STATUS_COMPLETED  = 'completed'
    STATUS_CANCELLED  = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_UPCOMING,  'Upcoming'),
        (STATUS_ONGOING,   'Ongoing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    course        = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='exams',
    )
    name          = models.CharField(max_length=200)
    exam_type     = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    exam_date     = models.DateField()
    total_marks   = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=40)
    academic_year = models.CharField(max_length=10, default='2025-26')
    semester      = models.IntegerField(default=1)
    status        = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_UPCOMING
    )
    instructions  = models.TextField(blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def get_average_marks(self):
        result = self.marks.aggregate(avg=Avg('marks_obtained'))
        return round(result['avg'], 1) if result['avg'] else None

    def get_pass_count(self):
        return self.marks.filter(marks_obtained__gte=self.passing_marks).count()

    def get_fail_count(self):
        return self.marks.filter(marks_obtained__lt=self.passing_marks).count()

    def __str__(self):
        return f"{self.course.code} — {self.name} ({self.exam_date})"

    class Meta:
        ordering = ['-exam_date']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'


class Mark(models.Model):
    """
    Stores marks obtained by a student in an exam.
    Grade is computed automatically from marks using compute_grade().
    """
    GRADE_CHOICES = [
        ('O',  'Outstanding (O)'),
        ('A+', 'Excellent (A+)'),
        ('A',  'Very Good (A)'),
        ('B+', 'Good (B+)'),
        ('B',  'Above Average (B)'),
        ('C',  'Average (C)'),
        ('P',  'Pass (P)'),
        ('F',  'Fail (F)'),
        ('AB', 'Absent'),
    ]

    student         = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='marks',
    )
    exam            = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='marks',
    )
    marks_obtained  = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    grade           = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    is_absent       = models.BooleanField(default=False)
    remarks         = models.CharField(max_length=200, blank=True, null=True)
    entered_by      = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='marks_entered',
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    @staticmethod
    def compute_grade(marks_obtained, total_marks):
        """
        Computes grade based on percentage.
        This is a pure service function — no DB calls.
        Demonstrates separating business logic from the model.
        """
        if total_marks == 0:
            return 'F'
        pct = (float(marks_obtained) / float(total_marks)) * 100
        if pct >= 90:   return 'O'
        elif pct >= 80: return 'A+'
        elif pct >= 70: return 'A'
        elif pct >= 60: return 'B+'
        elif pct >= 55: return 'B'
        elif pct >= 50: return 'C'
        elif pct >= 40: return 'P'
        else:           return 'F'

    def save(self, *args, **kwargs):
        if self.is_absent:
            self.grade = 'AB'
        else:
            self.grade = self.compute_grade(
                self.marks_obtained, self.exam.total_marks
            )
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        if self.exam.total_marks == 0:
            return 0
        return round((float(self.marks_obtained) / float(self.exam.total_marks)) * 100, 1)

    def get_grade_color(self):
        color_map = {
            'O': 'purple', 'A+': 'blue', 'A': 'teal',
            'B+': 'green', 'B': 'green', 'C': 'amber',
            'P': 'amber',  'F': 'red',   'AB': 'gray',
        }
        return color_map.get(self.grade, 'gray')

    def __str__(self):
        return f"{self.student.roll_number} | {self.exam} | {self.marks_obtained}"

    class Meta:
        unique_together = ('student', 'exam')
        ordering = ['-exam__exam_date']
        verbose_name = 'Mark'
        verbose_name_plural = 'Marks'


class ActivityLog(models.Model):
    """
    System-wide activity log.
    Written to by Django Signals — auto-records important events
    without any manual logging calls in views.

    Phase 7 teaching point: signals let you react to model events
    (save, delete) in a decoupled way.
    """
    ACTION_STUDENT_ENROLLED   = 'student_enrolled'
    ACTION_ATTENDANCE_LOW     = 'attendance_low'
    ACTION_FEE_PAID           = 'fee_paid'
    ACTION_FEE_OVERDUE        = 'fee_overdue'
    ACTION_RESULT_PUBLISHED   = 'result_published'
    ACTION_EXAM_CREATED       = 'exam_created'
    ACTION_USER_LOGIN         = 'user_login'

    ACTION_CHOICES = [
        (ACTION_STUDENT_ENROLLED, 'Student Enrolled'),
        (ACTION_ATTENDANCE_LOW,   'Low Attendance Alert'),
        (ACTION_FEE_PAID,         'Fee Payment Received'),
        (ACTION_FEE_OVERDUE,      'Fee Overdue'),
        (ACTION_RESULT_PUBLISHED, 'Result Published'),
        (ACTION_EXAM_CREATED,     'Exam Created'),
        (ACTION_USER_LOGIN,       'User Login'),
    ]

    COLOR_MAP = {
        ACTION_STUDENT_ENROLLED: 'blue',
        ACTION_ATTENDANCE_LOW:   'red',
        ACTION_FEE_PAID:         'green',
        ACTION_FEE_OVERDUE:      'amber',
        ACTION_RESULT_PUBLISHED: 'purple',
        ACTION_EXAM_CREATED:     'teal',
        ACTION_USER_LOGIN:       'gray',
    }

    action      = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    actor       = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='activity_logs',
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    @property
    def color(self):
        return self.COLOR_MAP.get(self.action, 'gray')

    def __str__(self):
        return f"[{self.action}] {self.description[:60]}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

