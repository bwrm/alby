# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.fields import empty
from shop.models.cart import CartModel
from shop.rest.money import MoneyField
from shop.serializers.bases import AvailabilitySerializer
from shop.serializers.defaults.catalog import AddToCartSerializer
from alby.models import VariantImage
from rest_framework import serializers
from alby.models import Fabric, ProductList



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

class AddSofaToCartSerializer(AddToCartSerializer):
    """
    Modified AddToCartSerializer which handles Sofas
    """
    def get_instance(self, context, data, extra_args):
        product = context['product']
        request = context['request']
        try:
            cart = CartModel.objects.get_from_request(request)
        except CartModel.DoesNotExist:
            cart = None
        try:
            variant = product.get_product_variant(product_code=data['product_code'])
        except (TypeError, KeyError, product.DoesNotExist):
            variant = product.variants.first()
        try:
            # TODO: change explicit model name no variant relation manager
            imgvar = VariantImage.objects.filter(product_id=variant.id)
            imglist = []
            imglist += [[i.image.url, j.image.thumbnails['admin_directory_listing_icon']] for [i, j] in zip(imgvar, imgvar)]
        except:
            imglist = 'default_img'

        instance = {
            'product': product.id,
            'product_code': variant.product_code,
            'unit_price': variant.unit_price,
            'is_in_cart': bool(product.is_in_cart(cart, product_code=variant.product_code)),
            'extra': {'fabric': variant.fabric.fabric_name, 'img': imglist},
            'availability': product.get_availability(request),

        }
        return instance

class UpdateDataSerialiser(serializers.Serializer):
    """
    Modified AddToCartSerializer which handles Sofas
    """
    fabric_name = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    fabric_type = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    composition = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    care = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")
    description = serializers.CharField(read_only=True, help_text="Exact product code of the cart item")

    def __init__(self, instance=None, data=empty, **kwargs):
        context = kwargs.get('context', {})
        instance = self.get_instance(context, data, kwargs)
        super(UpdateDataSerialiser, self).__init__(instance, data, context=context)

    def get_instance(self, context, data, extra_args):

        product = context['product']
        request = context['request']
        return {
            'fabric_name': product.fabric_name,
            'fabric_type': product.fabric_type,
            'composition': product.composition,
            'description': product.description,
            'care': product.care,
        }
