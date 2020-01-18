from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from phonenumber_field.phonenumber import to_python


def validate_phone_or_email(value):
    phone_number = to_python(value)
    error = ValidationError(_("The Phone number or Email entered is not valid. Phone number must have international format!"), code="invalid_phone_number_or_email")
    if not phone_number.is_valid():
        if validate_email(value) != None:
            raise error



