"""
GyanUday — Master API URL Configuration (Phase 5)

All REST endpoints are registered here.
Base URL: /api/

JWT Auth endpoints:
  POST /api/token/          → get access + refresh tokens
  POST /api/token/refresh/  → refresh access token
  POST /api/token/verify/   → verify a token

Students API:
  /api/students/            → CRUD
  /api/departments/         → CRUD
  /api/faculty/             → Read-only

Courses API:
  /api/courses/             → CRUD
  /api/enrollments/         → CRUD

Attendance API:
  /api/attendance/          → CRUD
  /api/attendance/summary/  → aggregated stats
  /api/attendance/department-stats/ → chart data
"""

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # ── JWT Token endpoints ──────────────────────────────────
    path('token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),
    path('token/verify/',  TokenVerifyView.as_view(),    name='token_verify'),

    # ── App API routes ───────────────────────────────────────
    path('', include('students.api_urls')),
    path('', include('courses.api_urls')),
    path('', include('attendance.api_urls')),
]
