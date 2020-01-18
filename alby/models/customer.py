# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
from shop.conf import app_settings
from shop.models.customer import BaseCustomer
from phonenumber_field.modelfields import PhoneNumberField



class Customer(BaseCustomer):
    """
    Default materialized model for Customer, adding a customer's number and phone number.

    If this model is materialized, then also register the corresponding serializer class
    :class:`shop.serializers.defaults.customer.CustomerSerializer`.
    """

    phone = PhoneNumberField(
        _('Phone number'),
        max_length=150,
        default=None,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Required. 150 characters or fewer. Digits and + only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    number = models.PositiveIntegerField(
        _("Customer Number"),
        null=True,
        default=None,
        unique=True,
    )

    def get_number(self):
        return self.number

    def get_phone(self):
        return self.phone

    def get_username(self):
        try:
            return self.user.get_username()
        except:
            return 'No provided'

    def get_or_assign_number(self):
        if self.number is None:
            aggr = Customer.objects.filter(number__isnull=False).aggregate(models.Max('number'))
            self.number = (aggr['number__max'] or 0) + 1
            self.save()
        return self.get_number()

    def as_text(self):
        template_names = [
            '{}/customer.txt'.format(app_settings.APP_LABEL),
            'alby/customer.txt',
        ]
        template = select_template(template_names)
        return template.render({'customer': self})
