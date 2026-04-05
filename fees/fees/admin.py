from django.contrib import admin
from .models import FeeStructure, Fee, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('department', 'academic_year', 'semester', 'total_fee')
    list_filter  = ('academic_year', 'department')


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display  = ('student', 'academic_year', 'semester', 'total_amount', 'status', 'due_date')
    list_filter   = ('status', 'academic_year', 'student__department')
    search_fields = ('student__roll_number', 'student__first_name', 'student__last_name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ('fee', 'amount', 'payment_date', 'method', 'status', 'received_by')
    list_filter   = ('method', 'status')
    search_fields = ('fee__student__roll_number', 'transaction_id')
