from django import forms
from .models import Payment, Booked, Tenants, Units, Issues
from django.core.exceptions import MultipleObjectsReturned

class Tenantform(forms.ModelForm):
    unit_type = forms.ModelChoiceField(queryset=Units.objects.filter(unt_availability=True))
    class Meta:
        model = Tenants
        fields = ['tent_name', 'tent_uname', 'unit_type', 'tent_emel', 'tent_pnum', 'tent_pword','assigned_unit']
    def __init__(self, *args, **kwargs):
        super(Tenantform, self).__init__(*args, **kwargs)
        self.fields['unit_type'].queryset = Units.objects.filter(unt_availability=True)

    def save(self, commit=True):
        tenant = super(Tenantform, self).save(commit=False)
        unit_type = self.cleaned_data['unit_type']
        available_units = Units.objects.filter(unt_availability=True)
        try:
            booked_unit = available_units.first()  # Get the first available unit
            if booked_unit:
                booked_unit.unt_availability = False
                booked_unit.save()
                tenant.assigned_unit = booked_unit
        except MultipleObjectsReturned:
            # Handle the case where multiple units are found
            # Get the first matching unit and update its availability
            first_matched_unit = available_units.first()
            if first_matched_unit:
                first_matched_unit.unt_availability = False
                first_matched_unit.save()
                tenant.assigned_unit = first_matched_unit
        if commit:
            tenant.save()
        return tenant

class Requestform(forms.ModelForm):
    class Meta:
        model = Booked
        fields = ['name', 'unit', 'pnum', 'date', 'emel', 'image', 'bookt']

class Paymentform(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['name', 'unit', 'mop', 'date', 'amount', 'ref', 'tenant']
        exclude = ['status']

class Compform(forms.ModelForm):
    class Meta:
        model = Issues
        fields = ['name', 'issue', 'solution']

class Propform(forms.ModelForm):
    class Meta:
        model = Units
        fields = ['unit_type', 'unit_blt', 'unt_price']

    def clean_email(self):
        unit_blt = self.cleaned_data.get('unit_blt')
        if Units.objects.filter(unit_blt=unit_blt).exists():
            raise forms.ValidationError("This unit already exist.")
        return unit_blt

