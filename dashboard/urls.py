from django.urls import path
from . import views
from .api_docs_view import api_docs

app_name = 'dashboard'

urlpatterns = [
    path('',     views.home,     name='home'),
    path('api/', api_docs,       name='api_docs'),
]
