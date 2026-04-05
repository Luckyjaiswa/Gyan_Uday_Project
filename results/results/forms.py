from django import forms
from .models import Exam, Mark


class ExamForm(forms.ModelForm):
    class Meta:
        model  = Exam
        fields = ('course', 'name', 'exam_type', 'exam_date', 'total_marks',
                  'passing_marks', 'academic_year', 'semester', 'status', 'instructions')
        widgets = {
            'course':        forms.Select(attrs={'class': 'form-control'}),
            'name':          forms.TextInput(attrs={'class': 'form-control'}),
            'exam_type':     forms.Select(attrs={'class': 'form-control'}),
            'exam_date':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_marks':   forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-26'}),
            'semester':      forms.NumberInput(attrs={'class': 'form-control'}),
            'status':        forms.Select(attrs={'class': 'form-control'}),
            'instructions':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MarkForm(forms.ModelForm):
    class Meta:
        model  = Mark
        fields = ('student', 'exam', 'marks_obtained', 'is_absent', 'remarks')
        widgets = {
            'student':        forms.Select(attrs={'class': 'form-control'}),
            'exam':           forms.Select(attrs={'class': 'form-control'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_absent':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks':        forms.TextInput(attrs={'class': 'form-control'}),
        }


class BulkMarkEntryForm(forms.Form):
    """Select exam to bulk-enter marks for all enrolled students."""
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.select_related('course').all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
