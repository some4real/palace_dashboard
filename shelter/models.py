#shelter/models.py

from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.core.exceptions import ValidationError
from django.utils import timezone

from account.models import Organization, Building, CustomUser

class Family(models.Model):
    name = models.CharField(max_length=255, help_text="Optional label for the family (e.g. 'Smith Family')")
    case_id = models.CharField(max_length=100)
    head_of_household = models.CharField(max_length=255)
    number_of_kids = models.IntegerField()
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='families', null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Family #{self.id}"
    

class Client(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]

    EMPLOYMENT_STATUS_CHOICES = [
        ('E', 'Employed'),
        ('U', 'Unemployed'),
        ('S', 'Student'),
        ('R', 'Retired'),
    ]
    #photo = models.ImageField(upload_to='logos/', null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='clients', null=True, blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='clients',
        null=False,  # Allow null values temporarily
        blank=True  # Allow blank values temporarily
    )
    building = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True, related_name='clients')
    case_id = models.CharField(max_length=100, blank=True, null=False)
    ssn = EncryptedCharField(max_length=11, null=True, unique=True, db_index=True, blank=True)
    phone_number = models.CharField(max_length=15, db_index=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True)
    disability_status = models.CharField(max_length=200, blank=True)
    employment_status = models.CharField(max_length=1, choices=EMPLOYMENT_STATUS_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_joined = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}) ({self.case_id})"

    def clean(self):
        if self.building and self.organization:
            if self.building.organization != self.organization:
                raise ValidationError("Building must belong to the same organization as the client.")

    @property
    def case_id(self):
        return self.family.case_id if self.family else None


    def save(self, *args, **kwargs):
        if self.building:
            self.organization = self.building.organization
        self.full_clean()
        if self.family:
            self.case_id = self.family.case_id
        super().save(*args, **kwargs)

class Shift(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='shifts')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shifts')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shift for {self.user.email} at {self.building.name} from {self.start_time} to {self.end_time}"
    
class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='created_reports')
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
    adult_count = models.IntegerField()
    child_count = models.IntegerField()
    family_count = models.IntegerField()
    absent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ClientPass(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='passes')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='passes')
    pass_type = models.CharField(max_length=50, choices=[
        ('temporary', 'Temporary'),
        ('permanent', 'Permanent'),
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    pass_reason = models.TextField()
    return_expected = models.DateTimeField()

    def __str__(self):
        return f"{self.building.name} - {self.count} clients"

class Case(models.Model):
    case_id = models.CharField(max_length=30, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cases')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='cases', null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.case_id} - {self.client.first_name} {self.client.last_name} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.case_id:
            org = self.client.organization or (self.family.organization if self.family else None)
            if not org:
                raise ValueError("Organization must be set through client or family to generate case_id.")
            
            org_code = org.code  # Make sure org has a unique code

            last_case = Case.objects.filter(client__organization=org).order_by('-id').first()
            next_number = 1
            if last_case and last_case.case_id.startswith(f"{org_code}-"):
                try:
                    last_number = int(last_case.case_id.split('-')[1])
                    next_number = last_number + 1
                except ValueError:
                    pass

            self.case_id = f"{org_code}-{next_number:05d}"
        
        super().save(*args, **kwargs)

        # Optional: sync with family
        if self.family:
            self.family.case_id = self.case_id
            self.family.save()
