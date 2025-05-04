#shelter/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/organization/settings/', views.organization_settings_view, name='organization_setting'),
    path('dashboard/client_list/', views.client_list, name='client_list'),
    path('sidebar/', views.dashboard_sidebar, name='dashboard_sidebar'),
    path('staff-list/', views.staff_list, name='staff_list'),
    path('dashboard/client/', views.client_list, name='client_list'),
]
