#account/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

import uuid
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import get_user_model

from .models import CustomUser 
from shelter.models import Client

@login_required
@permission_required('account.can_assign_roles', raise_exception=True)
def assign_role(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard') 

    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'supervisor', 'residential aide']:
            user.role = new_role
            user.save()
            messages.success(request, f"Role updated to {new_role}.")
            return redirect('dashboard')  
        else:
            messages.error(request, "Invalid role selected.")
    
    return render(request, 'account/assign_role.html', {'user': user})

@login_required
@permission_required('account.can_revoke_access', raise_exception=True)
def revoke_access(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard')  # Replace with your user list view name

    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, f"{user.email}'s access has been revoked.")
        return redirect('dashboard')  

    return render(request, 'account/revoke_access.html', {'user': user})

@login_required
@permission_required('account.can_delete_client_data', raise_exception=True)
def delete_client_data(request, client_id):
    # Assume you have a Client model related to CustomUser or elsewhere
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        messages.error(request, "Client not found.")
        return redirect('client_list')  # Redirect to the client list page

    if request.method == 'POST':
        client.delete()
        messages.success(request, f"Client data has been deleted.")
        return redirect('client_list')  # Redirect to the client list page

    return render(request, 'account/delete_client_data.html', {'client': client})

# Email Invite vIEW
def send_invite_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())

    # Send email with registration link
    mail_subject = 'Invite to Register'
    message = render_to_string('invite_email.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': uid,
        'token': token,
    })
    send_mail(mail_subject, message, 'admin@domain.com', [user.email])

# Registration View
def register_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        messages.error(request, "Invalid invitation link.")
        return redirect('home')  # Redirect to the home page

    if default_token_generator.check_token(user, token):
        # Allow the user to set their password and complete registration
        if request.method == 'POST':
            password = request.POST.get('password')
            user.set_password(password)
            user.save()
            messages.success(request, "Your account has been successfully created.")
            return redirect('login')

        return render(request, 'account/register.html', {'user': user})

    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('home')
