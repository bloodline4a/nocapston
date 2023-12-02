from django.contrib.auth.backends import ModelBackend
from .models import Tenants  # Import your Tenant model
import logging

class TenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            tenant = Tenants.objects.get(username=username)
            if tenant.check_password(password):
                logging.debug(f"Authentication succeeded for user {username}")
                return tenant
        except Tenants.DoesNotExist:
            pass

        logging.debug(f"Authentication failed for user {username}")
        return None

    def get_user(self, user_id):
        try:
            return Tenants.objects.get(pk=user_id)
        except Tenants.DoesNotExist:
            return None