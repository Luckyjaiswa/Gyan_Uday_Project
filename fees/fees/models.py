from django.db import models
from django.db.models import Sum
from students.models import Student


class FeeStructure(models.Model):
    """
    Defines the fee amount for a given academic year, semester and department.
    Admin sets this once per term; individual Fee records are generated from it.
    """
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]

    academic_year = models.CharField(max_length=10)   # e.g. "2025-26"
    semester      = models.IntegerField(choices=SEMESTER_CHOICES)
    department    = models.ForeignKey(
        'students.Department',
        on_delete=models.CASCADE,
        related_name='fee_structures',
    )
    tuition_fee   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_fee      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    library_fee   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_fee(self):
        return self.tuition_fee + self.exam_fee + self.library_fee + self.other_fee

    def __str__(self):
        return f"{self.department.code} | {self.academic_year} | Sem {self.semester}"

    class Meta:
        unique_together = ('academic_year', 'semester', 'department')
        ordering = ['-academic_year', 'semester']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'


class Fee(models.Model):
    """
    One fee record per student per semester.
    Tracks total due amount and links to all payments made.
    """
    STATUS_PENDING  = 'pending'
    STATUS_PARTIAL  = 'partial'
    STATUS_PAID     = 'paid'
    STATUS_OVERDUE  = 'overdue'
    STATUS_WAIVED   = 'waived'

    STATUS_CHOICES = [
        (STATUS_PENDING,  'Pending'),
        (STATUS_PARTIAL,  'Partially Paid'),
        (STATUS_PAID,     'Paid'),
        (STATUS_OVERDUE,  'Overdue'),
        (STATUS_WAIVED,   'Waived'),
    ]

    student       = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fees',
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    academic_year = models.CharField(max_length=10)
    semester      = models.IntegerField()
    total_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    due_date      = models.DateField()
    status        = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    remarks       = models.TextField(blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    @property
    def amount_paid(self):
        """Total amount paid so far — aggregates across all Payment records."""
        result = self.payments.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))
        return result['total'] or 0

    @property
    def amount_due(self):
        """Remaining balance."""
        return self.total_amount - self.amount_paid

    @property
    def is_fully_paid(self):
        return self.amount_due <= 0

    def update_status(self):
        """Recalculate and save status based on payments."""
        paid = self.amount_paid
        if paid <= 0:
            self.status = self.STATUS_PENDING
        elif paid >= self.total_amount:
            self.status = self.STATUS_PAID
        else:
            self.status = self.STATUS_PARTIAL
        self.save(update_fields=['status'])

    def get_status_color(self):
        color_map = {
            self.STATUS_PENDING: 'amber',
            self.STATUS_PARTIAL: 'blue',
            self.STATUS_PAID:    'green',
            self.STATUS_OVERDUE: 'red',
            self.STATUS_WAIVED:  'purple',
        }
        return color_map.get(self.status, 'gray')

    def __str__(self):
        return f"{self.student.roll_number} | {self.academic_year} Sem {self.semester}"

    class Meta:
        unique_together = ('student', 'academic_year', 'semester')
        ordering = ['-academic_year', 'semester']
        verbose_name = 'Fee'
        verbose_name_plural = 'Fees'


class Payment(models.Model):
    """
    Individual payment transaction for a Fee record.
    One Fee can have multiple partial Payments.
    """
    METHOD_CASH    = 'cash'
    METHOD_ONLINE  = 'online'
    METHOD_DD      = 'dd'
    METHOD_CHEQUE  = 'cheque'

    METHOD_CHOICES = [
        (METHOD_CASH,   'Cash'),
        (METHOD_ONLINE, 'Online Transfer'),
        (METHOD_DD,     'Demand Draft'),
        (METHOD_CHEQUE, 'Cheque'),
    ]

    STATUS_COMPLETED = 'completed'
    STATUS_PENDING   = 'pending'
    STATUS_FAILED    = 'failed'
    STATUS_REFUNDED  = 'refunded'

    STATUS_CHOICES = [
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PENDING,   'Pending'),
        (STATUS_FAILED,    'Failed'),
        (STATUS_REFUNDED,  'Refunded'),
    ]

    fee              = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount           = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date     = models.DateField()
    method           = models.CharField(max_length=10, choices=METHOD_CHOICES)
    transaction_id   = models.CharField(max_length=100, blank=True, null=True)
    status           = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
    )
    received_by      = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments_received',
    )
    remarks          = models.TextField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update the parent Fee status after each payment
        self.fee.update_status()

    def __str__(self):
        return f"₹{self.amount} | {self.fee.student.roll_number} | {self.payment_date}"

    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

