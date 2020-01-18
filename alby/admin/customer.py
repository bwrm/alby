# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.translation import ugettext_lazy as _
from shop.admin.customer import CustomerProxy, CustomerAdminBase
from shop.admin.customer import CustomerInlineAdminBase as BaseCustomerInlineAdminBase


class CustomerInlineAdmin(BaseCustomerInlineAdminBase):
    fieldsets = [
        (None, {'fields': ['get_number', ]}),
        (_("Addresses"), {'fields': ['get_shipping_addresses', 'get_billing_addresses']})
    ]
    readonly_fields = ['get_phone', 'get_number', 'get_shipping_addresses', 'get_billing_addresses']

    def get_number(self, customer):
        return customer.get_number() or '–'
    get_number.short_description = _("Customer Number")

    def get_number(self, customer):
        return customer.get_phone() or '–'
    get_number.short_description = _("Customer Phone")

    def get_shipping_addresses(self, customer):
        addresses = [(a.as_text(),) for a in customer.shippingaddress_set.all()]
        return format_html_join('', '<address>{0}</address>', addresses)
    get_shipping_addresses.short_description = _("Shipping")

    def get_billing_addresses(self, customer):
        addresses = [(a.as_text(),) for a in customer.billingaddress_set.all()]
        return format_html_join('', '<address>{0}</address>', addresses)
    get_billing_addresses.short_description = _("Billing")


@admin.register(CustomerProxy)
class CustomerAdmin(CustomerAdminBase):
    class Media:
        css = {'all': ['shop/css/admin/customer.css']}

    inlines = [CustomerInlineAdmin]

    def get_list_display(self, request):
        list_display = list(super(CustomerAdmin, self).get_list_display(request))
        return list_display

