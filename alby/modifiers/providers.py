# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http.response import HttpResponseRedirect
from shop.models.order import OrderModel, BaseOrder
from django.core.exceptions import ImproperlyConfigured
from shop.payment.providers import PaymentProvider
from shop.models.defaults.order import Order
import json


class PayWhenTake(PaymentProvider):
    """
    Provides a simple prepayment payment provider.
    """
    namespace = 'pay-when-take'

    def __init__(self):
        if (not (callable(getattr(BaseOrder, 'pay_when_take', None)))):
            # msg = "Missing methods in Order model. Add 'alby.modifiers.workflows.ShipThenPayWorkflowMixin' to SHOP_ORDER_WORKFLOWS."
            # raise ImproperlyConfigured(msg)
            pass
        super(PayWhenTake, self).__init__()

    def get_payment_request(self, cart, request):
        order = BaseOrder.objects.create_from_cart(cart, request)
        order.populate_from_cart(cart, request)
        order.ready_for_take()
        order.save(with_notification=True)
        return 'window.location.href="{}";'.format(order.get_absolute_url())
