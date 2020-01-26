# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import PositiveIntegerField, BooleanField
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from shop.models import order


class OrderItem(order.BaseOrderItem):
    """Default materialized model for OrderItem"""
    quantity = PositiveIntegerField(_("Ordered quantity"))
    canceled = BooleanField(default=False)


    class Meta:
        verbose_name = pgettext_lazy('order_models', "Ordered Item")
        verbose_name_plural = pgettext_lazy('order_models', "Ordered Items")
