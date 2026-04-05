from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import Fee, Payment, FeeStructure
from .forms import FeeForm, PaymentForm, FeeStructureForm
from students.models import Student


@login_required
def fee_list(request):
    """
    Lists all fee records with summary stats.
    ORM: aggregate Sum across related Payment records.
    """
    fees = (
        Fee.objects
        .select_related('student', 'student__department')
        .order_by('-academic_year', 'student__roll_number')
    )

    # Filter
    status_filter = request.GET.get('status')
    search        = request.GET.get('search', '')
    if status_filter:
        fees = fees.filter(status=status_filter)
    if search:
        fees = fees.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search)  |
            Q(student__roll_number__icontains=search)
        )

    # Summary stats using aggregate
    stats = Fee.objects.aggregate(
        total_due      = Sum('total_amount'),
        total_paid_sum = Sum('payments__amount',
                             filter=Q(payments__status='completed')),
        total_records  = Count('id'),
        pending_count  = Count('id', filter=Q(status__in=['pending', 'partial', 'overdue'])),
    )

    total_due     = stats['total_due']     or 0
    total_paid    = stats['total_paid_sum'] or 0
    total_pending = total_due - total_paid

    return render(request, 'fees/list.html', {
        'page_title':    'Fee Management',
        'fees':          fees,
        'total_due':     total_due,
        'total_paid':    total_paid,
        'total_pending': total_pending,
        'pending_count': stats['pending_count'],
        'status_filter': status_filter,
        'search':        search,
        'status_choices': Fee.STATUS_CHOICES,
    })


@login_required
def fee_detail(request, pk):
    """Shows all payments for a specific fee record."""
    fee      = get_object_or_404(Fee.objects.select_related('student', 'student__department'), pk=pk)
    payments = fee.payments.select_related('received_by').order_by('-payment_date')
    return render(request, 'fees/detail.html', {
        'page_title': f'Fee Detail — {fee.student.get_full_name()}',
        'fee':        fee,
        'payments':   payments,
    })


@login_required
def fee_create(request):
    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f'Fee record created for {fee.student.get_full_name()}.')
            return redirect('fees:detail', pk=fee.pk)
    else:
        form = FeeForm()
    return render(request, 'fees/form.html', {
        'page_title': 'Create Fee Record',
        'form': form,
        'action': 'Create',
    })


@login_required
def payment_create(request, fee_pk):
    """Record a new payment against an existing fee."""
    fee = get_object_or_404(Fee, pk=fee_pk)

    if fee.is_fully_paid:
        messages.info(request, 'This fee is already fully paid.')
        return redirect('fees:detail', pk=fee.pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.fee         = fee
            payment.received_by = request.user
            # Validate amount doesn't exceed remaining balance
            if payment.amount > fee.amount_due:
                form.add_error('amount',
                    f'Amount cannot exceed the remaining balance of ₹{fee.amount_due}.')
            else:
                payment.save()  # triggers fee.update_status() via model's save()
                messages.success(
                    request,
                    f'Payment of ₹{payment.amount} recorded for {fee.student.get_full_name()}.'
                )
                return redirect('fees:detail', pk=fee.pk)
    else:
        form = PaymentForm(initial={
            'payment_date': timezone.now().date(),
            'amount': fee.amount_due,
        })

    return render(request, 'fees/payment_form.html', {
        'page_title': f'Record Payment — {fee.student.get_full_name()}',
        'form': form,
        'fee':  fee,
    })


@login_required
def fee_structure_list(request):
    structures = FeeStructure.objects.select_related('department').order_by('-academic_year', 'semester')
    return render(request, 'fees/structure_list.html', {
        'page_title':  'Fee Structures',
        'structures':  structures,
    })


@login_required
def fee_structure_create(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            fs = form.save()
            messages.success(request, f'Fee structure created: {fs}')
            return redirect('fees:structure_list')
    else:
        form = FeeStructureForm()
    return render(request, 'fees/structure_form.html', {
        'page_title': 'Add Fee Structure',
        'form': form,
        'action': 'Create',
    })
