from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Profile

class PhoneBackend(ModelBackend):
    """
    Authenticates against Profile.phone_number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        phone_number = username # In our login form, the 'phone' field is submitted as 'username'
        if not phone_number:
            return None
        
        try:
            # Normalize phone number (digits only)
            normalized_phone = ''.join(filter(str.isdigit, str(phone_number)))
            profile = Profile.objects.get(phone_number=normalized_phone)
            user = profile.user
            if user.check_password(password):
                return user
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None
        return None
