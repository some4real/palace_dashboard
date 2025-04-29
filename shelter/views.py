from django.shortcuts import render
from .utils import get_current_shift

def dashboard(request):
    current_shift = get_current_shift()
    #current_building = "Building A"  # replace this with user-selected or session-based logic
    return render(request, 'shelter/dashboard.html', {
        'current_shift': current_shift,
        #'current_building': current_building,
    })


