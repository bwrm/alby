from django.db.models import CharField
from phoneauth.validators import validate_phone_or_email
from django.utils.translation import gettext_lazy as _



class PhoneEmailField(CharField):
    default_validators = [validate_phone_or_email]
    description = _("Email or Phone address")

    def __init__(self, *args, **kwargs):
        # max_length=254 to be compliant with RFCs 3696 and 5321
        kwargs.setdefault('max_length', 254)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # We do not exclude max_length if it matches default as we want to change
        # the default in future.
        return name, path, args, kwargs
