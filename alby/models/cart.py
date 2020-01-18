# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import SET_DEFAULT

from shop import deferred
from shop.models.address import BaseShippingAddress, BaseBillingAddress
from shop.models.cart import BaseCart


class Cart(BaseCart):
    """
    Default materialized model for BaseCart containing common fields
    """
    shipping_address = deferred.ForeignKey(
        BaseShippingAddress,
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
        related_name='+',
    )

    billing_address = deferred.ForeignKey(
        BaseBillingAddress,
        on_delete=SET_DEFAULT,
        null=True,
        default=None,
        related_name='+',
    )

    @property
    def total_weight(self):
        """
        Returns the total weight of all items in the cart (for Shipping Services).
        """
        rez = 0
        for item in self.items.all():
            try:
                rez += float(item.product.weight) * item.quantity
            except:
                pass
        return float("{0:.2f}".format(rez))
