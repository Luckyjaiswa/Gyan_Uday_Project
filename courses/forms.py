from django import forms
from .models import Course, Enrollment


class CourseForm(forms.ModelForm):
    class Meta:
        model  = Course
        fields = ('code', 'name', 'description', 'department', 'faculty',
                  'credits', 'semester', 'course_type', 'is_active')
        widgets = {
            'code':        forms.TextInput(attrs={'class': 'form-control'}),
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department':  forms.Select(attrs={'class': 'form-control'}),
            'faculty':     forms.Select(attrs={'class': 'form-control'}),
            'credits':     forms.NumberInput(attrs={'class': 'form-control'}),
            'semester':    forms.Select(attrs={'class': 'form-control'}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model  = Enrollment
        fields = ('student', 'course', 'is_active')
        widgets = {
            'student':   forms.Select(attrs={'class': 'form-control'}),
            'course':    forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
