from django.contrib import admin

from .models import Building, Client, Organization


admin.site.register(Organization)
admin.site.register(Building)
admin.site.register(Client)