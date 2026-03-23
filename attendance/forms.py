from django import forms
from .models import Attendance
from students.models import Student
from courses.models import Course


class AttendanceForm(forms.ModelForm):
    class Meta:
        model  = Attendance
        fields = ('student', 'course', 'date', 'status', 'remarks')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course':  forms.Select(attrs={'class': 'form-control'}),
            'date':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status':  forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BulkAttendanceForm(forms.Form):
    """
    Form for marking attendance for an entire class at once.
    The student list is rendered dynamically in the template.
    """
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )


class AttendanceFilterForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        required=False,
        empty_label='All Courses',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(status='active'),
        required=False,
        empty_label='All Students',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
