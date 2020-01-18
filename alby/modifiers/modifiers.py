# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from shop.modifiers.base import BaseCartModifier
from alby.modifiers.providers import NoPaymentRequired
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from shop.modifiers.pool import cart_modifiers_pool
from shop.modifiers.defaults import DefaultCartModifier
from shop.serializers.cart import ExtraCartRow
from shop.money import Money
from shop.shipping.modifiers import ShippingModifier
from shop.payment.modifiers import PaymentModifier
from shop.payment.providers import ForwardFundPayment


class PrimaryCartModifier(DefaultCartModifier):
    """
    Extended default cart modifier which handles the price for product variations
    """

    def process_cart_item(self, cart_item, request):
        variant = cart_item.product.get_product_variant(
            product_code=cart_item.product_code)
        cart_item.unit_price = variant.unit_price
        cart_item.line_total = cart_item.unit_price * cart_item.quantity
        try:
            rebate = cart_item.product.get_rebate(cart_item.quantity)
            cart_item.line_total = cart_item.line_total - (cart_item.line_total * rebate) / 100
            cart_item.unit_price = cart_item.unit_price - (cart_item.unit_price * rebate) / 100
        except:
            pass
        # grandparent super
        return super(DefaultCartModifier, self).process_cart_item(cart_item, request)


class PostalShippingModifier(ShippingModifier):
    identifier = 'postal-shipping'

    def get_choice(self):
        return (self.identifier, _("Postal shipping"))

    def add_extra_cart_row(self, cart, request):
        if not self.is_active(cart.extra.get('shipping_modifier')) and len(cart_modifiers_pool.get_shipping_modifiers()) > 1:
            return
        # add a shipping flat fee
        amount = Money('5')
        if cart.total_weight<1:
            amount = Money('4')
        elif cart.total_weight >=1 and cart.total_weight < 3:
            amount = Money('7.5')
        elif cart.total_weight >=3 and cart.total_weight < 15:
            amount = Money('10')
        elif cart.total_weight >=15 and cart.total_weight < 30:
            amount = Money('20')
        elif cart.total_weight > 30:
            amount = Money('500')
        else:
            amount = Money('999')

        instance = {'label': _("Shipping costs"), 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount

    def ship_the_goods(self, delivery):
        if not delivery.shipping_id:
            raise ValidationError("Please provide a valid Shipping ID")
        super(PostalShippingModifier, self).ship_the_goods(delivery)

class CourierModifier(ShippingModifier):
    identifier = 'courier-delivery'

    def get_choice(self):
        return (self.identifier, _("Courier delivery. Onliy within Minsk"))

    def add_extra_cart_row(self, cart, request):
        if not self.is_active(cart) and len(cart_modifiers_pool.get_shipping_modifiers()) > 1:
            return
        # add a shipping flat fee
        amount = Money('3')
        instance = {'label': _("Courier shipping costs"), 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount



"""
Payment Modifiers
"""

class PayByCardModifier(PaymentModifier):
    """
    This modifiers has no influence on the cart final. It can be used,
    to enable the customer to pay the products on delivery.
    """
    identifier = 'card-payment'

    payment_provider = ForwardFundPayment()

    def get_choice(self):
        return (self.payment_provider.namespace, _("Pay by card"))


class PayWhenTakeModifier(PaymentModifier):
    """
    This modifiers has no influence on the cart final. It can be used,
    to enable the customer to pay the products on delivery.
    """
    payment_provider = NoPaymentRequired()

    def get_choice(self):
        return (self.payment_provider.namespace, _("Pay when taking"))
