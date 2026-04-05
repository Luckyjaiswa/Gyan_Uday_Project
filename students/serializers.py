"""
students/serializers.py

DRF Serializers — Phase 5

Key concepts taught here:
- ModelSerializer     : auto-generates fields from the model
- SerializerMethodField : adds computed/read-only fields
- Nested serializers  : embed related objects instead of just IDs
- read_only_fields    : fields the API returns but won't accept on write
- validate_<field>()  : field-level custom validation
- validate()          : object-level cross-field validation
"""

from rest_framework import serializers
from .models import Student, Department, FacultyProfile
from accounts.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializes Department with a computed student_count field.
    Used both standalone and nested inside StudentSerializer.
    """
    student_count = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = ('id', 'name', 'code', 'description', 'student_count')

    def get_student_count(self, obj):
        # SerializerMethodField calls get_<field_name>(self, obj)
        return obj.students.count()


class StudentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for the student LIST endpoint.
    Returns only the fields needed for a list view — keeps responses fast.
    """
    department_name  = serializers.CharField(source='department.name', read_only=True)
    department_code  = serializers.CharField(source='department.code', read_only=True)
    full_name        = serializers.SerializerMethodField()
    status_display   = serializers.CharField(source='get_status_display', read_only=True)
    attendance_pct   = serializers.SerializerMethodField()

    class Meta:
        model  = Student
        fields = (
            'id', 'roll_number', 'full_name', 'first_name', 'last_name',
            'email', 'department_name', 'department_code',
            'year', 'semester', 'status', 'status_display', 'attendance_pct',
        )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_attendance_pct(self, obj):
        return obj.get_attendance_percentage()


class StudentDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for CREATE / UPDATE / RETRIEVE of a single student.
    Includes nested department object and all fields.
    """
    department_detail = DepartmentSerializer(source='department', read_only=True)
    full_name         = serializers.SerializerMethodField()
    attendance_pct    = serializers.SerializerMethodField()
    status_display    = serializers.CharField(source='get_status_display', read_only=True)
    gender_display    = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model  = Student
        fields = (
            'id', 'roll_number', 'full_name',
            'first_name', 'last_name', 'email', 'phone',
            'gender', 'gender_display', 'date_of_birth', 'blood_group',
            'address', 'photo',
            'department', 'department_detail',
            'year', 'semester', 'status', 'status_display',
            'guardian_name', 'guardian_phone',
            'admission_date', 'created_at', 'updated_at',
            'attendance_pct',
        )
        read_only_fields = ('admission_date', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_attendance_pct(self, obj):
        return obj.get_attendance_percentage()

    # ── Field-level validation ─────────────────────────────────
    def validate_roll_number(self, value):
        """
        Ensure roll number is uppercase.
        validate_<field_name> is called automatically by DRF.
        """
        return value.upper()

    def validate_email(self, value):
        """Ensure email is lowercase."""
        return value.lower()

    # ── Object-level validation ────────────────────────────────
    def validate(self, data):
        """
        Cross-field validation: semester must match year range.
        Year 1 → Semesters 1-2, Year 2 → 3-4, etc.
        validate() is called after all field validations pass.
        """
        year = data.get('year', getattr(self.instance, 'year', None))
        sem  = data.get('semester', getattr(self.instance, 'semester', None))
        if year and sem:
            expected_sems = [(year * 2) - 1, year * 2]
            if sem not in expected_sems:
                raise serializers.ValidationError(
                    f"Year {year} students should be in semester {expected_sems[0]} or {expected_sems[1]}."
                )
        return data


class FacultyProfileSerializer(serializers.ModelSerializer):
    full_name   = serializers.CharField(source='user.get_full_name', read_only=True)
    email       = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model  = FacultyProfile
        fields = (
            'id', 'employee_id', 'full_name', 'email',
            'department', 'department_name',
            'designation', 'qualification', 'joining_date', 'specialization',
        )
