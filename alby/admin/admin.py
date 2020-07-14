# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.template.context import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from filer.models import ThumbnailOption
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
# from shop.admin.defaults import customer
from alby.admin import customer
from shop.models.defaults.order import Order
# from alby.models.order import Order
from alby.admin.order import OrderAdmin as BaseOrderAdmin
from shop.admin.order import PrintInvoiceAdminMixin
from shop.admin.delivery import DeliveryOrderAdminMixin
from adminsortable2.admin import SortableAdminMixin, PolymorphicSortableAdminMixin
from shop.admin.product import CMSPageAsCategoryMixin, UnitPriceMixin, ProductImageInline, InvalidateProductCacheMixin, CMSPageFilter
from polymorphic.admin import (PolymorphicParentModelAdmin, PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter)
from alby.models import Product, Commodity, SofaModel, SofaVariant
from alby.models import CommodityInventory, Lamel, Discount, LamelInventory, Fabric, VariantImage
from nested_inline.admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline
from adminsortable2.admin import SortableInlineAdminMixin


admin.site.site_header = "ALBY Administration"
admin.site.unregister(ThumbnailOption)


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin, PrintInvoiceAdminMixin, DeliveryOrderAdminMixin):
    list_display = ['get_number', 'customer', 'status_name', 'get_total', 'created_at']


__all__ = ['customer']

from shop.models.related import ProductPageModel, ProductImageModel


class ProductImageInlineNested(admin.StackedInline):
    model = ProductImageModel
    inlines = []
    extra = 1


class VariantImageInline(NestedTabularInline):
    model = VariantImage
    fk_name = 'product'
    extra = 1

from django import forms

class SofaVariantForm(forms.ModelForm):
    unit_price = forms.DecimalField(required=False, decimal_places = 2)

    def __init__(self, *args, **kwargs):
        super(SofaVariantForm, self).__init__(*args, **kwargs)
        self.fields['unit_price'].widget.attrs['min'] = 0.01

    def clean_unit_price(self):
        price = self.cleaned_data['unit_price']
        if price and price < 0.0099:
            raise forms.ValidationError("Price cannot be less than 0.01")
        return price

    class Meta:
        model = SofaVariant
        fields = '__all__'

class SofaVariantInLine(NestedStackedInline):
    model = SofaVariant
    inlines = [VariantImageInline, ]
    fk_name = 'product_model'
    readonly_fields = ['product_code',]
    can_delete = True
    extra = 1
    save_as = True
    form = SofaVariantForm




class CommodityInventoryAdmin(admin.StackedInline):
    model = CommodityInventory
    extra = 0

class LamelInventoryAdmin(admin.StackedInline):
    model = LamelInventory
    extra = 0


@admin.register(Commodity)
class CommodityAdmin(InvalidateProductCacheMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                     PlaceholderAdminMixin, CMSPageAsCategoryMixin, PolymorphicChildModelAdmin):
    """
    Since our Commodity model inherits from polymorphic Product, we have to redefine its admin class.
    """
    base_model = Product
    fields = [
        ('product_name', 'slug'),
        ('product_code', 'unit_price'),
        'active',
    ]
    readonly_fields = ['product_code',]
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInline, CommodityInventoryAdmin]
    prepopulated_fields = {'slug': ['product_name']}


@admin.register(Lamel)
class LamelAdmin(InvalidateProductCacheMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                 CMSPageAsCategoryMixin, PlaceholderAdminMixin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': [
                ('product_name', 'slug'),
                ('product_code', 'unit_price'),
                ('active', 'discont_scheme'),
            ],
        }),
        (_("Translatable Fields"), {
            'fields': ['caption', 'description'],
        }),
        (_("Properties"), {
            'fields': ['lamel_width', 'is_lamel', 'weight_by_hand', 'length', 'depth', 'weight'],
        }),
    )
    readonly_fields = ['product_code',]
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInline, LamelInventoryAdmin]
    prepopulated_fields = {'slug': ['product_name']}
    save_as = True

@admin.register(Fabric)
class FabricAdmin(InvalidateProductCacheMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                     CMSPageAsCategoryMixin, PlaceholderAdminMixin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': [
                ('product_name', 'slug'),
                ('product_code', 'unit_price'),
                ('active'),
            ],
        }),
        (_("Translatable Fields"), {
            'fields': ['caption', 'description'],
        }),
        (_("Properties"), {
            'fields': [ 'composition', 'care', 'fabric_type'],
        }),
    )
    readonly_fields = ['product_code',]
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInline, ]
    prepopulated_fields = {'slug': ['product_name']}
    save_as = True

@admin.register(SofaModel)
class SofaModelAdmin(InvalidateProductCacheMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                 CMSPageAsCategoryMixin, PlaceholderAdminMixin, PolymorphicChildModelAdmin, NestedModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': [
                ('product_name', 'slug'),
            ],
        }),
        (_("Translatable Fields"), {
            'fields': ['caption', 'description'],
        }),
        (_("Properties"), {
            'fields': ['sofa_type'],
        }),
    )
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInlineNested, SofaVariantInLine]
    prepopulated_fields = {'slug': ['product_name']}
    save_as = True


admin.site.register(Discount)

@admin.register(Product)
class ProductAdmin(PolymorphicSortableAdminMixin, PolymorphicParentModelAdmin):
    base_model = Product
    child_models = [Commodity, Lamel, SofaModel, Fabric]
    list_display = ['product_name', 'get_price', 'product_type', 'active']
    list_display_links = ['product_name']
    search_fields = ['product_name']
    list_filter = [PolymorphicChildModelFilter, CMSPageFilter]
    list_per_page = 250
    list_max_show_all = 1000

    def get_price(self, obj):
        return str(obj.get_real_instance().get_price(None))

    get_price.short_description = _("Price starting at")

