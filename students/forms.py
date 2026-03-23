from django import forms
from .models import Student, Department, FacultyProfile


class DepartmentForm(forms.ModelForm):
    class Meta:
        model  = Department
        fields = ('name', 'code', 'hod', 'description')
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'code':        forms.TextInput(attrs={'class': 'form-control'}),
            'hod':         forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model  = Student
        fields = (
            'roll_number', 'first_name', 'last_name', 'email', 'phone',
            'gender', 'date_of_birth', 'blood_group', 'address', 'photo',
            'department', 'year', 'semester', 'status',
            'guardian_name', 'guardian_phone',
        )
        widgets = {
            'roll_number':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':         forms.TextInput(attrs={'class': 'form-control'}),
            'gender':        forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group':   forms.Select(attrs={'class': 'form-control'}),
            'address':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo':         forms.FileInput(attrs={'class': 'form-control'}),
            'department':    forms.Select(attrs={'class': 'form-control'}),
            'year':          forms.Select(attrs={'class': 'form-control'}),
            'semester':      forms.Select(attrs={'class': 'form-control'}),
            'status':        forms.Select(attrs={'class': 'form-control'}),
            'guardian_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model  = FacultyProfile
        fields = ('employee_id', 'department', 'designation',
                  'qualification', 'joining_date', 'specialization')
        widgets = {
            'employee_id':    forms.TextInput(attrs={'class': 'form-control'}),
            'department':     forms.Select(attrs={'class': 'form-control'}),
            'designation':    forms.TextInput(attrs={'class': 'form-control'}),
            'qualification':  forms.TextInput(attrs={'class': 'form-control'}),
            'joining_date':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StudentFilterForm(forms.Form):
    """Search and filter form for the student list page."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or roll number...',
        }),
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    year = forms.ChoiceField(
        choices=[('', 'All Years')] + Student.YEAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Student.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
