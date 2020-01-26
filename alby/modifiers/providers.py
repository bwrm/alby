# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http.response import HttpResponseRedirect
from shop.models.order import OrderModel, BaseOrder
from django.core.exceptions import ImproperlyConfigured
from shop.payment.providers import PaymentProvider
import json
from shop.models.defaults.order import Order


class PayWhenTake(PaymentProvider):
    """
    Creating order witount payment? customer pay when taking order.
    """
    namespace = 'pay-when-take'

    # def __init__(self):
    #     if (not (callable(getattr(OrderModel, 'created', None)))):
    #         msg = "Missing methods in OrderModel model. Add 'alby.modifiers.workflows.PayWhenTakeyWorkflowMixin' to SHOP_ORDER_WORKFLOWS."
    #         raise ImproperlyConfigured(msg)
    #         pass
    #     super(PayWhenTake, self).__init__()

    def get_payment_request(self, cart, request):
        order = OrderModel.objects.create_from_cart(cart, request)
        order.populate_from_cart(cart, request)
        order.save(with_notification=True)
        return 'window.location.href="{}";'.format(order.get_absolute_url())

class PayAtPostProvider(PaymentProvider):
    """
    Creating order with pay when delivery on post.
    """
    namespace = 'pay-at-post'

    # def __init__(self):
    #     if (not (callable(getattr(OrderModel, 'created', None)))):
    #         msg = "Missing methods in OrderModel model. Add 'alby.modifiers.workflows.PayWhenTakeyWorkflowMixin' to SHOP_ORDER_WORKFLOWS."
    #         raise ImproperlyConfigured(msg)
    #         pass
    #     super(PayWhenTake, self).__init__()

    def get_payment_request(self, cart, request):
        order = OrderModel.objects.create_from_cart(cart, request)
        order.populate_from_cart(cart, request)
        order.save(with_notification=True)
        return 'window.location.href="{}";'.format(order.get_absolute_url())
