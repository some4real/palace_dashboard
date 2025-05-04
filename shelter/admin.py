#account/admin.py

from django.contrib import admin

from .models import Building, Case, Client, ClientCount, Family
from .models import Report, Round, Organization, ClientPass, Shift


admin.site.register(Organization)
admin.site.register(Building)

class ClientAdmin(admin.ModelAdmin):
    #exclude = ('organization',)  # Hide organization from form
    list_display = ('first_name', 'last_name', 'family', 'organization', 'building', 'case_id')
    list_filter = ('organization', 'building', 'family')
    def save_model(self, request, obj, form, change):
        if not obj.organization and hasattr(request.user, 'organization'):
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

admin.site.register(Client, ClientAdmin)
admin.site.register(Family)
admin.site.register(Case)
admin.site.register(Report)
admin.site.register(Round)
admin.site.register(ClientCount)
admin.site.register(ClientPass)
admin.site.register(Shift)

