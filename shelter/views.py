#shelter/views.py

from django.shortcuts import render
from .utils import get_current_shift

def dashboard(request):
    current_shift = get_current_shift()
    #current_building = "Building A"  # replace this with user-selected or session-based logic
    return render(request, 'shelter/dashboard.html', {
        'current_shift': current_shift,
        #'current_building': current_building,
    })

def client_list(request):
    # This is a placeholder. You would typically fetch this from your database.
    clients = [
        {'name': 'John Doe', 'status': 'Active'},
        {'name': 'Jane Smith', 'status': 'Inactive'},
        # Add more client data as needed
    ]
    return render(request, 'shelter/client_list.html', {'clients': clients})

