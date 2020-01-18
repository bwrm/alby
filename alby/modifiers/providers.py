# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http.response import HttpResponseRedirect
from shop.models.order import OrderModel, BaseOrder
from django.core.exceptions import ImproperlyConfigured
# from shop.payment.providers import PaymentProvider
from alby.models.order import Order

import json


class NoPaymentRequired(object):
    """
    Provides a simple prepayment payment provider.
    """
    namespace = 'no-payment-required'

    def get_urls(self):
        """
        Return a list of URL patterns for external communication with the payment service provider.
        """
        return []

    def __init__(self):
        if (not (callable(getattr(Order, 'pay_when_take', None)))):
            # msg = "Missing methods in Order model. Add 'alby.modifiers.workflows.ShipThenPayWorkflowMixin' to SHOP_ORDER_WORKFLOWS."
            # raise ImproperlyConfigured(msg)
            pass
        super(NoPaymentRequired, self).__init__()

    def get_payment_request(self, cart, request):
        order = Order.objects.create_from_cart(cart, request)
        order.populate_from_cart(cart, request)
        order.ready_for_take()
        order.save(with_notification=True)
        return 'window.location.href="{}";'.format(order.get_absolute_url())
