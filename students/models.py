from django.db import models
from django.core.validators import RegexValidator
from accounts.models import User


class Department(models.Model):
    """
    Represents an academic department (e.g. CS & IT, Engineering).
    Students and Courses are linked to a Department.
    """
    name       = models.CharField(max_length=100, unique=True)
    code       = models.CharField(max_length=10, unique=True)
    hod        = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'faculty'},
        related_name='headed_departments',
    )
    description = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def student_count(self):
        return self.students.count()

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class Student(models.Model):
    """
    Core student profile model.
    Each student is linked to a User account (OneToOne)
    and belongs to a Department.
    """

    STATUS_ACTIVE      = 'active'
    STATUS_INACTIVE    = 'inactive'
    STATUS_GRADUATED   = 'graduated'
    STATUS_DROPPED     = 'dropped'

    STATUS_CHOICES = [
        (STATUS_ACTIVE,    'Active'),
        (STATUS_INACTIVE,  'Inactive'),
        (STATUS_GRADUATED, 'Graduated'),
        (STATUS_DROPPED,   'Dropped'),
    ]

    GENDER_MALE    = 'M'
    GENDER_FEMALE  = 'F'
    GENDER_OTHER   = 'O'

    GENDER_CHOICES = [
        (GENDER_MALE,   'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER,  'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+','AB+'),('AB-','AB-'),
    ]

    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 5)]
    SEM_CHOICES  = [(i, f'Semester {i}') for i in range(1, 9)]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True, blank=True,
    )
    roll_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-]+$',
                message='Roll number must be uppercase letters, digits, or hyphens only.'
            )
        ],
        help_text='e.g. CS2024001',
    )
    first_name    = models.CharField(max_length=50)
    last_name     = models.CharField(max_length=50)
    email         = models.EmailField(unique=True)
    phone         = models.CharField(max_length=15, blank=True, null=True)
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group   = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    address       = models.TextField(blank=True, null=True)
    photo         = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    department    = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='students',
    )
    year           = models.IntegerField(choices=YEAR_CHOICES, default=1)
    semester       = models.IntegerField(choices=SEM_CHOICES,  default=1)
    admission_date = models.DateField(auto_now_add=True)
    status         = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    guardian_name  = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=15,  blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        return (self.first_name[0] + self.last_name[0]).upper()

    def get_status_color(self):
        color_map = {
            self.STATUS_ACTIVE:    'green',
            self.STATUS_INACTIVE:  'amber',
            self.STATUS_GRADUATED: 'blue',
            self.STATUS_DROPPED:   'red',
        }
        return color_map.get(self.status, 'gray')

    def get_attendance_percentage(self):
        try:
            from attendance.models import Attendance
            total   = Attendance.objects.filter(student=self).count()
            if total == 0:
                return None
            present = Attendance.objects.filter(student=self, status='present').count()
            return round((present / total) * 100, 1)
        except Exception:
            return None

    def __str__(self):
        return f"{self.get_full_name()} ({self.roll_number})"

    class Meta:
        ordering = ['roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


class FacultyProfile(models.Model):
    """Extended profile for faculty members."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='faculty_profile',
        limit_choices_to={'role': 'faculty'},
    )
    employee_id    = models.CharField(max_length=20, unique=True)
    department     = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='faculty_members',
    )
    designation    = models.CharField(max_length=100, blank=True)
    qualification  = models.CharField(max_length=200, blank=True)
    joining_date   = models.DateField(blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.designation}"

    class Meta:
        ordering = ['user__first_name']
        verbose_name = 'Faculty Profile'
        verbose_name_plural = 'Faculty Profiles'
