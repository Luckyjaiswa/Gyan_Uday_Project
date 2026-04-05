from django import forms
from .models import Fee, Payment, FeeStructure


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model  = FeeStructure
        fields = ('academic_year', 'semester', 'department',
                  'tuition_fee', 'exam_fee', 'library_fee', 'other_fee')
        widgets = {
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-26'}),
            'semester':      forms.Select(attrs={'class': 'form-control'}),
            'department':    forms.Select(attrs={'class': 'form-control'}),
            'tuition_fee':   forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'exam_fee':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'library_fee':   forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_fee':     forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class FeeForm(forms.ModelForm):
    class Meta:
        model  = Fee
        fields = ('student', 'academic_year', 'semester', 'total_amount', 'due_date', 'remarks')
        widgets = {
            'student':       forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-26'}),
            'semester':      forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount':  forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model  = Payment
        fields = ('amount', 'payment_date', 'method', 'transaction_id', 'remarks')
        widgets = {
            'amount':         forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'method':         forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks':        forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
