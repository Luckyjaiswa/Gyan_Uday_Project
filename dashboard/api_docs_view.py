from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def api_docs(request):
    context = {
        'page_title': 'API Reference',

        'student_endpoints': [
            {'method': 'GET',   'url': '/api/students/',                    'desc': 'List all students'},
            {'method': 'POST',  'url': '/api/students/',                    'desc': 'Create student'},
            {'method': 'GET',   'url': '/api/students/1/',                  'desc': 'Get one student'},
            {'method': 'PATCH', 'url': '/api/students/1/',                  'desc': 'Update student'},
            {'method': 'GET',   'url': '/api/students/at-risk/',            'desc': 'Below 75% attendance'},
            {'method': 'GET',   'url': '/api/students/1/attendance-report/','desc': 'Full att. breakdown'},
            {'method': 'GET',   'url': '/api/departments/',                 'desc': 'List departments'},
            {'method': 'GET',   'url': '/api/faculty/',                     'desc': 'List faculty'},
        ],
        'course_endpoints': [
            {'method': 'GET',  'url': '/api/courses/',                       'desc': 'List courses'},
            {'method': 'POST', 'url': '/api/courses/',                       'desc': 'Create course'},
            {'method': 'GET',  'url': '/api/courses/1/',                     'desc': 'Course detail'},
            {'method': 'GET',  'url': '/api/courses/1/enrolled-students/',   'desc': 'Enrolled students'},
            {'method': 'GET',  'url': '/api/enrollments/',                   'desc': 'List enrollments'},
            {'method': 'POST', 'url': '/api/enrollments/',                   'desc': 'Enroll a student'},
        ],
        'attendance_endpoints': [
            {'method': 'GET',  'url': '/api/attendance/',                    'desc': 'List records'},
            {'method': 'POST', 'url': '/api/attendance/',                    'desc': 'Mark attendance'},
            {'method': 'GET',  'url': '/api/attendance/summary/?course=1',   'desc': 'Course summary'},
            {'method': 'GET',  'url': '/api/attendance/department-stats/',   'desc': 'Dept. averages'},
        ],
        'auth_endpoints': [
            {'method': 'POST', 'url': '/api/token/',         'desc': 'Get access + refresh token'},
            {'method': 'POST', 'url': '/api/token/refresh/', 'desc': 'Refresh access token'},
            {'method': 'POST', 'url': '/api/token/verify/',  'desc': 'Verify a token'},
        ],
    }
    return render(request, 'api/docs.html', context)
