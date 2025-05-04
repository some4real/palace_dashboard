#shelter/views.py

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .utils import get_current_shift
from django.contrib.auth.decorators import login_required, permission_required
from .models import Family, Client, Case, Shift, Report, ClientCount
from account.models import Building, CustomUser, Organization, Role
from django.core.paginator import Paginator

from datetime import datetime


def index(request):
    return render(request, 'shelter/index.html')


@login_required
def dashboard_view(request):
    user = request.user
    org = user.organization
    building = getattr(user, 'building', None)

    families = Family.objects.filter(building=building).count()
    clients = Client.objects.filter(building=building).count()
    open_cases = Case.objects.filter(status='open', client__building=building).count()
    shifts = Shift.objects.filter(user=user).order_by('-start_time')[:5]
    reports = Report.objects.filter(created_by=user).order_by('-created_at')[:5]

    # Common data
    total_clients = Client.objects.filter(organization=org).count()
    total_users = CustomUser.objects.filter(organization=org).count()
    total_buildings = Building.objects.filter(organization=org).count()

    roles = Role.objects.filter(organization=org) if user.role == 'admin' else None
    user_list = CustomUser.objects.filter(organization=org).exclude(id=user.id).order_by('name') if user.is_admin() else []
    paginator = Paginator(user_list, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Determine the greeting based on the time of day
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    context = {
        'greeting': greeting,
        'total_clients': total_clients,
        'total_users': total_users,
        'total_buildings': total_buildings,
        'user_list': [],
        'org': org,
        'families': families,
        'clients': clients,
        'open_cases': open_cases,
        'shifts': shifts,
        'reports': reports,
        'user': user,
        'roles': roles,
        'page_obj': page_obj,
    }

    if user.is_admin():
        # Admin-only data
        staff = CustomUser.objects.filter(organization=org).exclude(id=user.id).order_by('name')
        context['user_list'] = staff
    return render(request, 'shelter/dashboard.html', context)

@login_required
def organization_settings_view(request):
    org = request.user.organization

    # Ensure only admins can assign roles
    if not request.user.role or request.user.role.name.lower() != 'admin':
        print(f"Redirecting user {request.user.email} to dashboard due to insufficient permissions.")
        messages.error(request, "You do not have permission.")
        return redirect('dashboard')

    if request.method == 'POST':
        print("Updating organization settings...")
        org.name = request.POST.get('name')
        org.code = request.POST.get('code')
        if 'logo' in request.FILES:
            org.logo = request.FILES['logo']
        org.save()
        messages.success(request, "Organization settings updated.")

    return render(request, 'shelter/organization_setting.html', {'organization': org})


@login_required
def dashboard_sidebar(request):
    return render(request, 'shelter/dashboard_sidebar.html', {
        'user': request.user,
        'organization': request.user.organization,
    })

@login_required
def staff_list(request):
    if request.user.role.name.lower() != 'admin':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    users = CustomUser.objects.filter(organization=request.user.organization).order_by('-id')
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'account/staff_list.html', {'page_obj': page_obj})


from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Client

@login_required
def client_list(request):
    search_query = request.GET.get('search', '')
    case_id_query = request.GET.get('case_id', '')

    user_org = request.user.organization
    clients = Client.objects.select_related('family').prefetch_related('cases').filter(organization=user_org)

    if case_id_query:
        clients = clients.filter(cases__case_id__icontains=case_id_query)

    if search_query:
        clients = clients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(family__name__icontains=search_query) |
            #Q(case_id__icontains=search_query) |
            Q(cases__case_id__icontains=search_query)
        ).distinct()

    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shelter/client_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'case_id_query': case_id_query,
    })

