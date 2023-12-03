from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

class Admin(models.Model):
    uname = models.CharField(max_length=255, default='admin_username')
    pword = models.CharField(max_length=255, default='admin_password')

    def save(self, *args, **kwargs):
        # Set a default password if none is provided
        if not self.pword:
            self.pword = make_password('admin_password')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.uname
    
    
class Issues(models.Model):
    name = models.CharField(max_length=255)
    issue = models.CharField(max_length=255)
    solution = models.CharField(max_length=255)

class Units(models.Model):
    unit_type = models.CharField(max_length=255)
    unit_blt = models.CharField(max_length=255, default='location')
    unt_price = models.FloatField()
    unt_availability = models.BooleanField(default=True) 

    def availability_display(self):
        return "Vacant" if self.unt_availability else "Occupied"
    
    def __str__(self):
        return self.unit_type

class Booked(models.Model):
    APPROVAL_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    bookt = models.CharField(max_length=255,default='duration')
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    pnum = models.CharField(max_length=20)  
    date = models.DateField(max_length=255)
    emel = models.CharField(max_length=255, validators=[EmailValidator()], default='custom@example.com')  
    image = models.ImageField(upload_to='images/',default='image')
    ref = models.IntegerField(default=1)
    mop = models.CharField(max_length=255, default='CASH')  
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')

class Payment(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref = models.IntegerField()
    mop = models.CharField(max_length=255)  
    unit = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    tenant = models.ForeignKey('Tenants', on_delete=models.CASCADE)  
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('successful', 'Successful'),
            ('decline', 'Decline')
        ],
        default='Pending'
    )
    
class Tenants(AbstractUser):
    tent_name = models.CharField(max_length=255)
    tent_uname = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=255)
    tent_pnum = models.CharField(max_length=20)  
    tent_emel = models.EmailField(max_length=255, validators=[EmailValidator()], default='custom@example.com')
    tent_pword = models.CharField(max_length=255)
    assigned_unit = models.ForeignKey(Units, on_delete=models.SET_NULL, null=True, blank=True)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created (not updated)
            # Check if there is an available unit of the specified type
            booked_unit = Units.objects.filter(unit_type=self.unit_type, unt_availability=True).first()
            if booked_unit:
                # Check if the unit is not already assigned to another tenant
                if not Tenants.objects.filter(assigned_unit=booked_unit).exists():
                    # If the tenant already has an assigned unit, reset its availability to 'True'
                    if self.assigned_unit and self.assigned_unit.unt_availability == False:
                        self.assigned_unit.unt_availability = True
                        self.assigned_unit.save()
                    booked_unit.unt_availability = False
                    booked_unit.save()
                    self.assigned_unit = booked_unit
                else:
                    # Handle the case where the unit is already assigned to another tenant
                    raise Exception("Selected unit is already assigned to another tenant.")
            else:
                # Handle the case where no available unit is found
                raise Exception("No available unit found with the specified type.")

            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.assigned_unit and not self.assigned_unit.unt_availability:
            # Set the availability of the unit to 'True'
            self.assigned_unit.unt_availability = True
            self.assigned_unit.save()

        # Call the superclass delete method to delete the tenant
        super().delete(*args, **kwargs)


    def __str__(self):
        return self.tent_name

User.groups.field.remote_field.related_name = 'user_groups'
User.user_permissions.field.remote_field.related_name = 'user_permissions'
Tenants.groups.field.remote_field.related_name = 'tenant_groups'
Tenants.user_permissions.field.remote_field.related_name = 'tenant_permissions'

