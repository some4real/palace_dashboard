#account/models.py

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField

class Organization(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    logo = CloudinaryField(
        'logo', null=True, blank=True, default='https://res.cloudinary.com/dlhvy3thk/image/upload/v1746075089/logo-placeholder-image_i8iizd.png')
    
    def save(self, *args, **kwargs):
            if not self.slug:
                base_slug = slugify(self.name)
                slug = base_slug
                num = 1
                while Organization.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{num}"
                    num += 1
                self.slug = slug
            super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Role name
    organization = models.ForeignKey(
        'Organization', on_delete=models.CASCADE, related_name='roles'
    )  # Link roles to an organization

    # Enforce uniqueness within an organization
    class Meta:
            unique_together = ('name', 'organization')

    def __str__(self):
        return self.name
    
class Building(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='buildings')

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    photo = CloudinaryField(
        'photo', null=True, blank=True, default='https://res.cloudinary.com/dlhvy3thk/image/upload/v1720723272/coodomqszlct7aqwxtcn.jpg'
    )

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='users'
    )
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name='users', null=True, blank=True
    )
    role = models.ForeignKey(
        'account.Role', on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )  # Link the user to a role dynamically
    is_active = models.BooleanField(default=True)
    is_admin_field = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['organization']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def is_admin(self):
        return self.role and self.role.name.lower() == 'admin'

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        # Only allow superusers to access the Django admin
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        # Only allow superusers to have permissions in the Django admin
        return self.is_superuser

    class Meta:
        permissions = [
            ("can_assign_roles", "Can assign roles to users"),
            ("can_revoke_access", "Can revoke user access"),
            ("can_delete_client_data", "Can delete client data"),
        ]

