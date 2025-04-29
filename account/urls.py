# account/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='account/login.html'), name='login'),
    path('register/<uidb64>/<token>/', views.register_user, name='register_user'),
    path('assign-role/<int:user_id>/', views.assign_role, name='assign_role'),
    path('revoke-access/<int:user_id>/', views.revoke_access, name='revoke_access'),
    path('delete-client/<int:client_id>/', views.delete_client_data, name='delete_client_data'),
]

