# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.fields import empty
from shop.models.cart import CartModel
from shop.rest.money import MoneyField
from shop.serializers.bases import AvailabilitySerializer
from shop.serializers.defaults.catalog import AddToCartSerializer



class RebateAddToCartSerializer(AddToCartSerializer):
    """
    By default, this serializer is used by the view class :class:`shop.views.catalog.AddToCartView`,
    which handles the communication from the "Add to Cart" dialog box.

    If a product has variations, which influence the fields in the "Add to Cart" dialog box, then
    this serializer shall be overridden by a customized implementation. Such a customized "*Add to
    Cart*" serializer has to be connected to the ``AddToCartView``. This usually is achieved in
    the projects ``urls.py`` by changing the catalog's routing to:
    ```
    urlpatterns = [
        ...
        url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view(
            serializer_class=CustomAddToCartSerializer,
        )),
        ...
    ]
    ```
    """

    def get_instance(self, context, data, extra):
        """
        Method calculate product's subtotal price depending on order quantity
        """

        product = context['product']
        request = context['request']
        unit_price = product.get_price(context['request'])
        try:
            extra = data.get('extra', {})
            subtotal_price = data.get('quantity') * unit_price
        except:
            instance = {
                'product': product.id,
                'product_code': product.product_code,
                'unit_price': unit_price,
                'subtotal': unit_price,
                'availability': product.get_availability(request, **extra),
            }
            return instance

        try:
            rebate = product.get_rebate(data.get('quantity'))
            price = unit_price * data.get('quantity')
            subtotal_price = price - (price * rebate) / 100
            unit_price = unit_price - (unit_price * rebate) / 100
        except:
            pass

        instance = {
            'product': product.id,
            'product_code': product.product_code,
            'unit_price': unit_price,
            'subtotal': subtotal_price,
            'extra': extra,
            'availability': product.get_availability(request, **extra),
        }
        return instance

