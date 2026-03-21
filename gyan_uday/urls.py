"""
GyanUday University — Root URL Configuration
Each app registers its own urls.py and is included here.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Redirect root to dashboard
    path('', lambda request: redirect('dashboard:home'), name='root'),

    # App URLs (uncomment as you build each phase)
    path('accounts/', include('accounts.urls')),        # Phase 2
    path('dashboard/', include('dashboard.urls')),      # Phase 1 (basic) + Phase 6 (full)
    path('students/', include('students.urls')),        # Phase 3
    path('courses/', include('courses.urls')),          # Phase 4
    path('attendance/', include('attendance.urls')),    # Phase 4
    path('fees/', include('fees.urls')),                # Phase 6
    path('results/', include('results.urls')),          # Phase 7

    # DRF API endpoints
    path('api/', include('gyan_uday.api_urls')),        # Phase 5
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
