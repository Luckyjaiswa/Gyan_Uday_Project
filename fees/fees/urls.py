from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('',                       views.fee_list,             name='list'),
    path('create/',                views.fee_create,           name='create'),
    path('<int:pk>/',              views.fee_detail,           name='detail'),
    path('<int:fee_pk>/pay/',      views.payment_create,       name='payment_create'),
    path('structures/',            views.fee_structure_list,   name='structure_list'),
    path('structures/create/',     views.fee_structure_create, name='structure_create'),
]
