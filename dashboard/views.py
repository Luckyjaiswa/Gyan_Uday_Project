"""
Dashboard Views
Phase 1: Returns hardcoded context so the template renders with dummy data.
Phase 6: This view will be replaced with real DB aggregations.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """
    Main dashboard view.
    Phase 1 — hardcoded data so the UI renders immediately.
    Phase 6 — replace context values with real ORM queries.
    """
    context = {
        'page_title': 'Academic Overview',
        'academic_year': '2025–26',
        'semester': 'Semester IV',

        # ── KPI cards ──────────────────────────────────────────────
        'total_students': 3248,
        'total_students_delta': '+4.2%',
        'total_students_delta_type': 'up',

        'avg_attendance': 82.4,
        'avg_attendance_delta': '+1.8%',
        'avg_attendance_delta_type': 'up',

        'fee_collected': '₹1.4 Cr',
        'fee_delta': '3.1% pending',
        'fee_delta_type': 'down',

        'active_courses': 64,
        'total_departments': 8,

        # ── Recent students (Phase 3: replace with Student.objects.all()) ──
        'recent_students': [
            {'name': 'Arjun Kumar',     'initials': 'AK', 'dept': 'CS & IT',     'attendance': 91, 'status': 'Active'},
            {'name': 'Priya Mishra',    'initials': 'PM', 'dept': 'Commerce',     'attendance': 74, 'status': 'Low Att.'},
            {'name': 'Rohan Verma',     'initials': 'RV', 'dept': 'Engineering',  'attendance': 88, 'status': 'Active'},
            {'name': 'Neha Sharma',     'initials': 'NS', 'dept': 'Arts & Sci.',  'attendance': 61, 'status': 'At Risk'},
            {'name': 'Siddharth Tiwari','initials': 'ST', 'dept': 'CS & IT',     'attendance': 95, 'status': 'Active'},
        ],

        # ── Activity feed (Phase 7: replace with real signals/log) ──
        'activities': [
            {'color': 'green',  'text': 'Result sheet published — CS-401 Data Structures',        'time': '2 min ago',   'by': 'Prof. K. Srivastava'},
            {'color': 'red',    'text': 'Neha Sharma attendance dropped below 65% threshold',     'time': '18 min ago',  'by': 'Auto-alert'},
            {'color': 'blue',   'text': '12 new students enrolled in MBA Sem 1',                  'time': '1 hr ago',    'by': 'Admissions Office'},
            {'color': 'amber',  'text': 'Fee reminder sent to 47 students (pending dues)',        'time': '3 hrs ago',   'by': 'Finance Dept.'},
            {'color': 'purple', 'text': 'Timetable updated — Sem IV Mid-Sem Exams schedule',      'time': 'Yesterday',   'by': 'Examination Cell'},
        ],

        # ── Chart data (Phase 6: fetch from API) ──
        'chart_labels': ['S1 22', 'S2 22', 'S1 23', 'S2 23', 'S1 24', 'S2 24', 'S1 25', 'S2 25'],
        'chart_cs':         [320, 330, 360, 375, 400, 420, 460, 480],
        'chart_engineering':[280, 290, 300, 315, 320, 340, 360, 375],
        'chart_commerce':   [200, 210, 215, 220, 230, 235, 240, 248],
        'chart_arts':       [160, 165, 170, 175, 180, 190, 200, 210],

        'dept_labels': ['CS & IT', 'Engineering', 'Commerce', 'Arts & Sci.', 'Others'],
        'dept_data':   [32, 28, 18, 14, 8],
    }
    return render(request, 'dashboard/home.html', context)
