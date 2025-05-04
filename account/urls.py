# account/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views 
from .views import CustomLoginView
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('register/', views.register_org, name='reg_org'),
    path('register/<uidb64>/<token>/', views.register_user, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),
    path('assign-role/<int:user_id>/', views.assign_role, name='assign_role'),
    path('reassign-role/<int:user_id>/', views.reassign_role, name='reassign_role'),
    path('revoke-access/<int:user_id>/', views.revoke_access, name='revoke_access'),
    path('delete-client/<int:client_id>/', views.delete_client_data, name='delete_client_data'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),
    path('profile/', views.profile_view, name='profile'),
    path('delete-staff/<int:user_id>/', views.delete_staff, name='delete_staff'),
    ]