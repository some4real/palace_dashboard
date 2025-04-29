# #account/management/commands/createsuperuser.py

from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management.base import CommandError
from account.models import Organization

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Prompt for organization
        organization_id = int(input("Organization (Organization.id): "))
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise CommandError(f"Organization with id {organization_id} does not exist.")

        # Pass the organization to the superuser creation process
        options['organization'] = organization
        super().handle(*args, **options)