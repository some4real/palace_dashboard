#account/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.conf import settings
from django.contrib.messages import get_messages
from .forms import ProfileForm

import uuid
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import EmailAuthenticationForm



from .models import CustomUser, Organization, Role, Building
from shelter.models import Client
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class CustomPasswordResetConfirmView(LoginRequiredMixin, auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'

class CustomPasswordResetCompleteView(LoginRequiredMixin, auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'

@login_required
def manage_roles(request):
    if request.user.role.name.lower() != 'admin':
        messages.error(request, "You do not have permission to manage roles.")
        return redirect('dashboard')

    organization = request.user.organization
    roles = Role.objects.filter(organization=organization)

    if request.method == 'POST':
        role_name = request.POST.get('role_name').strip() 
        # Check for duplicate roles within the same organization
        if Role.objects.filter(name__iexact=role_name, organization=organization).exists():
            messages.error(request, "Role already exists in your organization.")
        else:
            Role.objects.create(name=role_name, organization=organization)
            messages.success(request, f"Role '{role_name}' has been added.")

    return render(request, 'account/manage_roles.html', {'roles': roles})

@login_required
def assign_role(request, user_id=None):
    if not request.user.role or request.user.role.name.lower() != 'admin':

        messages.error(request, "You do not have permission to assign roles.")
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        role_id = request.POST.get('role')  # Get role ID from the form

        # Validate the email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect('assign_role', user_id=user_id)

        # Check if the role exists in the admin's organization
        try:
            role = Role.objects.get(id=role_id, organization=request.user.organization)
        except Role.DoesNotExist:
            messages.error(request, "Invalid role selected.")
            return redirect('assign_role', user_id=user_id)

        # Check if the user already exists
        user = CustomUser.objects.filter(email=email).first()

        if user:
            if user.organization == request.user.organization:
                # Update the role if the user belongs to the same organization
                user.role = role
                user.save()
                messages.success(request, f"{email}'s role has been updated to {role}.")
            else:
                messages.error(request, f"A user with the email {email} already exists.")
        else:
            user = CustomUser.objects.create(
                email=email,
                organization=request.user.organization,
                role=role,
                is_active=False,
            )
            send_invite_email(user, request)  # ✅ Send the email
            messages.success(request, f"Invite sent to {email} with the role of {role}.")

        return redirect('dashboard')

    # Fetch roles for the admin's organization
    roles = Role.objects.filter(organization=request.user.organization)
    return render(request, 'account/assign_role.html', {'roles': roles})

@login_required
def reassign_role(request, user_id):
    if request.user.role.name.lower() != 'admin':
        messages.error(request, "You do not have permission to reassign roles.")
        return redirect('staff_list')

    try:
        user_reassign = CustomUser.objects.get(id=user_id, organization=request.user.organization)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard')

    if request.method == 'POST':
        role_id = request.POST.get('role')  # Get the selected role ID from the form

        # Check if the role exists in the admin's organization
        try:
            role = Role.objects.get(id=role_id, organization=request.user.organization)
        except Role.DoesNotExist:
            messages.error(request, "Invalid role selected.")
            return redirect('reassign_role', user_id=user_id)
        
        # Reactivate the user if previously deactivated
        user_reassign.is_active = True

        # Update the user's role
        user_reassign.role = role

        # Update permissions based on the role
        if role.name.strip().lower() == 'admin':
            user_reassign.is_staff = True
            user_reassign.is_superuser = True
        else:
            user_reassign.is_staff = False
            user_reassign.is_superuser = False


        user_reassign.save()
        messages.success(request, f"{user_reassign.email}'s role has been updated to {role}.")
        return redirect('staff_list')

    # Fetch roles for the admin's organization
    roles = Role.objects.filter(organization=request.user.organization)
    return render(request, 'account/assign_role.html', {
        'roles': roles,
        'user': user_reassign,
        'is_reassign': True
    })

@login_required
def revoke_access(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard')  

    if request.method == 'POST':
        user.is_active = False
        user.save()
        messages.success(request, f"{user.email}'s access has been revoked.")
        return redirect('staff_list')  

    return render(request, 'account/revoke_access.html', {'user': user})

def delete_staff(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('delete_staff') 
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"{user.email}'s account has been deleted.")
        return redirect('dashboard')  

    return render(request, 'account/delete_user.html', {'user': user})

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

    domain = request.get_host()

    # Send email with registration link
    mail_subject = 'Invite to Register'
    message = render_to_string('account/invite_email.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': uid,
        'token': token,
    })
    send_mail(
    subject=mail_subject,
    message=message,  # fallback plain text
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[user.email],
    html_message=message  
)


# Registration View for Admin
@transaction.atomic
def register_org(request):
    if request.method == 'POST':
        org_name = request.POST.get('organization')
        name = request.POST.get('name')
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.", extra_tags="reg_org")
            return redirect('reg_org')

        # Create the organization
        org = Organization.objects.create(name=org_name)

        # Create the "admin" role for the organization if it doesn't exist
        admin_role, created = Role.objects.get_or_create(name='admin', organization=org)

        # Create the user as the organization admin
        user = CustomUser.objects.create(
            email=email,
            name=name,
            organization=org,
            role=admin_role,  # Assign the "admin" role
            is_staff=True,  # Allow access to application-specific admin features
            is_superuser=False,  # Prevent access to the Django admin panel
        )
        user.set_password(password)
        user.save()

        messages.success(request, "Organization and admin account created successfully.")
        return redirect('login')

    return render(request, 'account/reg_org.html')


# Registration View for User
def register_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        messages.error(request, "Invalid invitation link.")
        return redirect('index')

    if default_token_generator.check_token(user, token):
        if request.method == 'POST':
            name = request.POST.get('name')
            password = request.POST.get('password')
            user.name=name
            user.set_password(password)
            user.is_active = True  
            user.save()
            messages.success(request, "Your account has been successfully created.")
            return redirect('login')

        return render(request, 'account/register.html', {'user': user})

    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('dashboard')
    

class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=user)

    return render(request, 'account/profile.html', {'form': form})

@login_required
def delete_staff(request, user_id):
    if request.user.role.name.lower() != 'admin':
        messages.error(request, "You do not have permission to delete users.")
        return redirect('staff_list')

    try:
        user = CustomUser.objects.get(id=user_id, organization=request.user.organization)
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard')

    if request.method == 'POST':
        user.delete()
        messages.success(request, f"{user.email} has been deleted from the system.")
        return redirect('staff_list')

    return render(request, 'account/delete_staff.html', {'user': user})




