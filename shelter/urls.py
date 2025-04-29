#shelter/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/client_list/', views.client_list, name='client_list'),
]
