from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model for GyanUday University.
    Extends Django's AbstractUser with role, phone, and profile picture.
    Used as AUTH_USER_MODEL across the entire project.
    """

    # ── Roles ──────────────────────────────────────────────────────
    ROLE_ADMIN   = 'admin'
    ROLE_FACULTY = 'faculty'
    ROLE_STUDENT = 'student'

    ROLE_CHOICES = [
        (ROLE_ADMIN,   'Admin'),
        (ROLE_FACULTY, 'Faculty'),
        (ROLE_STUDENT, 'Student'),
    ]

    # ── Extra fields ───────────────────────────────────────────────
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )
    address = models.TextField(
        blank=True,
        null=True,
    )

    # ── Helpers ────────────────────────────────────────────────────
    def get_role_display_label(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'User')

    def get_initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.username[:2].upper()

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_faculty(self):
        return self.role == self.ROLE_FACULTY

    def is_student_user(self):
        return self.role == self.ROLE_STUDENT

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display_label()})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['first_name', 'last_name']

