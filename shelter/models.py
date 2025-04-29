from django.db import models
from fernet_fields import EncryptedCharField

from account.models import Organization, Building, CustomUser

#Client
class Client(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='clients')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='clients')
    ssn = EncryptedCharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return self.name
    
class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_reports')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='reports')

    def __str__(self):
        return self.title
    
class Round(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rounds')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rounds')
    created_at = models.DateTimeField(auto_now_add=True)
    
class ClientCount(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='client_counts')
    count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.building.name} - {self.count} clients"
    