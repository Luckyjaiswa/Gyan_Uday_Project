"""
students/api_urls.py

DRF Router — automatically generates these URLs:
  GET    /api/students/                → StudentViewSet.list()
  POST   /api/students/                → StudentViewSet.create()
  GET    /api/students/<pk>/           → StudentViewSet.retrieve()
  PUT    /api/students/<pk>/           → StudentViewSet.update()
  PATCH  /api/students/<pk>/           → StudentViewSet.partial_update()
  DELETE /api/students/<pk>/           → StudentViewSet.destroy()
  GET    /api/students/<pk>/attendance-report/ → custom @action
  GET    /api/students/at-risk/        → custom @action

  GET    /api/departments/             → DepartmentViewSet.list()
  ...etc

  GET    /api/faculty/                 → FacultyViewSet.list()
  GET    /api/faculty/<pk>/            → FacultyViewSet.retrieve()
"""

from rest_framework.routers import DefaultRouter
from .api_views import StudentViewSet, DepartmentViewSet, FacultyViewSet

router = DefaultRouter()
router.register(r'students',    StudentViewSet,    basename='student')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'faculty',     FacultyViewSet,    basename='faculty')

urlpatterns = router.urls
