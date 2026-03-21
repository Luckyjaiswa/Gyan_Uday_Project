"""
GyanUday — API URL Configuration (Phase 5)
All REST API endpoints are registered here using DRF routers.
This file is a stub in Phase 1; fully populated in Phase 5.
"""

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # App-level API routes (added phase by phase)
    # path('students/', include('students.api_urls')),
    # path('courses/', include('courses.api_urls')),
    # path('attendance/', include('attendance.api_urls')),
    # path('fees/', include('fees.api_urls')),
    # path('results/', include('results.api_urls')),
]
