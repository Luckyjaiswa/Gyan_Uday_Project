"""
results/signals.py — Phase 7

Django Signals — Key concepts:
- post_save    : fires AFTER a model instance is saved (create or update)
- pre_save     : fires BEFORE a model instance is saved
- post_delete  : fires AFTER a model instance is deleted
- sender       : the model class whose saves trigger this signal
- created      : True if this is a new record, False if an update
- receiver     : the function that handles the signal
- @receiver    : decorator that connects a handler to a signal

Why signals?
  Without signals, you'd have to manually add logging calls inside
  every view that creates a Student, Payment, Mark etc.
  With signals, the logging happens automatically whenever the model
  is saved — even from the admin panel, shell, or API.

This file is connected in results/apps.py via ready().
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


# ─────────────────────────────────────────────────────────────
# Signal 1: Log when a new Student is enrolled
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender='students.Student')
def log_student_enrolled(sender, instance, created, **kwargs):
    """
    Fires after every Student save.
    created=True  → brand new student record
    created=False → existing student was updated (skip)
    """
    if not created:
        return
    try:
        from results.models import ActivityLog
        ActivityLog.objects.create(
            action=ActivityLog.ACTION_STUDENT_ENROLLED,
            description=(
                f"{instance.get_full_name()} ({instance.roll_number}) "
                f"enrolled in {instance.department.name}."
            ),
        )
    except Exception:
        pass  # Never let a signal crash the main request


# ─────────────────────────────────────────────────────────────
# Signal 2: Low attendance alert when Attendance record saved
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender='attendance.Attendance')
def check_low_attendance(sender, instance, created, **kwargs):
    """
    After each attendance record, check if the student's overall
    attendance has dropped below 75%. If so, log an alert.
    Only fires on new records (not updates) to avoid spam.
    """
    if not created:
        return
    try:
        from results.models import ActivityLog
        from attendance.models import Attendance

        pct = Attendance.get_student_percentage(instance.student)
        if pct is not None and pct < 75:
            # Avoid duplicate alerts — check if we already logged one today
            from django.utils import timezone
            today = timezone.now().date()
            already_alerted = ActivityLog.objects.filter(
                action=ActivityLog.ACTION_ATTENDANCE_LOW,
                description__contains=instance.student.roll_number,
                created_at__date=today,
            ).exists()
            if not already_alerted:
                ActivityLog.objects.create(
                    action=ActivityLog.ACTION_ATTENDANCE_LOW,
                    description=(
                        f"{instance.student.get_full_name()} "
                        f"({instance.student.roll_number}) attendance "
                        f"dropped to {pct}% — below 75% threshold."
                    ),
                )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Signal 3: Log when a fee payment is completed
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender='fees.Payment')
def log_fee_payment(sender, instance, created, **kwargs):
    """
    Fires after a Payment is saved.
    Logs completed payments to the activity feed.
    """
    if not created:
        return
    if instance.status != 'completed':
        return
    try:
        from results.models import ActivityLog
        ActivityLog.objects.create(
            action=ActivityLog.ACTION_FEE_PAID,
            description=(
                f"Payment of ₹{instance.amount} received from "
                f"{instance.fee.student.get_full_name()} "
                f"({instance.fee.student.roll_number}) via {instance.get_method_display()}."
            ),
            actor=instance.received_by,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Signal 4: Log when a result (Mark) is published
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender='results.Mark')
def log_result_published(sender, instance, created, **kwargs):
    """
    Fires after a Mark record is saved.
    Only logs on creation (first entry of marks).
    """
    if not created:
        return
    try:
        from results.models import ActivityLog
        ActivityLog.objects.create(
            action=ActivityLog.ACTION_RESULT_PUBLISHED,
            description=(
                f"Result entered for {instance.student.get_full_name()} "
                f"in {instance.exam.course.code} — {instance.exam.name}: "
                f"{instance.marks_obtained}/{instance.exam.total_marks} ({instance.grade})."
            ),
            actor=instance.entered_by,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Signal 5: Log when an Exam is created
# ─────────────────────────────────────────────────────────────
@receiver(post_save, sender='results.Exam')
def log_exam_created(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        from results.models import ActivityLog
        ActivityLog.objects.create(
            action=ActivityLog.ACTION_EXAM_CREATED,
            description=(
                f"Exam scheduled: {instance.name} for "
                f"{instance.course.code} on {instance.exam_date}."
            ),
        )
    except Exception:
        pass
