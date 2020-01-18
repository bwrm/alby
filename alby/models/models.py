# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from djangocms_text_ckeditor.fields import HTMLField
from polymorphic.query import PolymorphicQuerySet
from parler.managers import TranslatableManager, TranslatableQuerySet
from parler.models import TranslatableModelMixin, TranslatedFieldsModel, TranslatedFields
from parler.fields import TranslatedField
from cms.models.fields import PlaceholderField
from shop.money import Money, MoneyMaker
from shop.money.fields import MoneyField
from shop.models.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin
from shop.models.inventory import BaseInventory, AvailableProductMixin
from alby.models.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.order import BaseOrderItem
from shop.models.defaults.delivery import Delivery
from shop.models.defaults.delivery_item import DeliveryItem
from shop.models.defaults.mapping import ProductPage, ProductImage
from alby.models.address import BillingAddress, ShippingAddress
from alby.models.customer import Customer
from alby.models.discount import Discount

__all__ = ['Cart', 'CartItem', 'Order', 'Delivery', 'DeliveryItem',
           'BillingAddress', 'ShippingAddress', 'Customer', ]


class OrderItem(BaseOrderItem):
    quantity = models.PositiveIntegerField(_("Ordered quantity"))
    canceled = models.BooleanField(_("Item canceled "), default=False)

    def populate_from_cart_item(self, cart_item, request):
        super(OrderItem, self).populate_from_cart_item(cart_item, request)
        # the product's unit_price must be fetched from the product's variant
        try:
            variant = cart_item.product.get_product_variant(
                product_code=cart_item.product_code)
            self._unit_price = Decimal(variant.unit_price)
        except (KeyError, ObjectDoesNotExist) as e:
            raise CartItem.DoesNotExist(e)


class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class ProductManager(BaseProductManager, TranslatableManager):
    queryset_class = ProductQuerySet

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db)
        return qs.prefetch_related('translations')


@python_2_unicode_compatible
class Product(CMSPageReferenceMixin, TranslatableModelMixin, BaseProduct):
    """
    Base class to describe a polymorphic product. Here we declare common fields available in all of
    our different product types. These common fields are also used to build up the view displaying
    a list of all products.
    """
    product_name = models.CharField(
        _("Product Name"),
        max_length=255,
    )

    slug = models.SlugField(
        _("Slug"),
        unique=True,
    )

    caption = TranslatedField()

    # controlling the catalog
    order = models.PositiveIntegerField(
        _("Sort by"),
        db_index=True,
    )

    cms_pages = models.ManyToManyField(
        'cms.Page',
        through=ProductPage,
        help_text=_("Choose list view this product shall appear on."),
    )

    images = models.ManyToManyField(
        'filer.Image',
        through=ProductImage,
    )

    class Meta:
        ordering = ('order',)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    objects = ProductManager()

    # filter expression used to lookup for a product item using the Select2 widget
    lookup_fields = ['product_name__icontains']

    def __str__(self):
        return self.product_name

    @property
    def sample_image(self):
        return self.images.first()


class ProductTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='translations',
        null=True,
    )

    caption = HTMLField(
        verbose_name=_("Caption"),
        blank=True,
        null=True,
        configuration='CKEDITOR_SETTINGS_CAPTION',
        help_text=_(
            "Short description used in the catalog's list view of products."),
    )

    class Meta:
        unique_together = [('language_code', 'master')]


class Commodity(AvailableProductMixin, Product):
    """
    This Commodity model inherits from polymorphic Product, and therefore has to be redefined.
    """
    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        unique=True,
    )

    # controlling the catalog
    placeholder = PlaceholderField("Commodity Details")
    show_breadcrumb = True  # hard coded to always show the product's breadcrumb

    default_manager = TranslatableManager()

    class Meta:
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    def get_price(self, request):
        return self.unit_price


class CommodityInventory(BaseInventory):
    product = models.ForeignKey(
        Commodity,
        on_delete=models.CASCADE,
        related_name='inventory_set',
    )

    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Available quantity in stock")
    )


@python_2_unicode_compatible
class Lamel(AvailableProductMixin, Product):
    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
    )

    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )

    LAM_WIDTH = (('38', '38 mm'), ('53', '53 mm'), ('63', '63 mm'), ('68', '68 mm'))

    lamel_width = models.CharField(
        _('width'),
        default=53,
        max_length=6,
        choices=LAM_WIDTH,
        help_text=_("Lamels width")
    )

    length = models.CharField(
        _("Lamel's length"),
        max_length=25,
        blank=True,
    )

    depth = models.CharField(
        _("Lamel's depth"),
        max_length=25,
        blank=True,
    )

    weight = models.CharField(
        _('weight'),
        default=0,
        max_length=6,
        help_text=_("Weight of item, kg")
    )
    is_lamel = models.BooleanField(
        _("Lamel"),
        default=True,
        help_text=_("Is this lamel (for calculating weight)."),
    )

    weight_by_hand = models.BooleanField(
        _("Enter weight by hand"),
        default=False,
        help_text=_("For enter lamel weight by hand"),
    )

    discont_scheme = models.ForeignKey(Discount, blank=True, null=True, on_delete=models.CASCADE)

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        blank=True,
    )

    default_manager = ProductManager()

    class Meta:
        verbose_name = _("Lamel")
        verbose_name_plural = _("Lamels")

    def is_unique_scu(self, scu):
        scu = str(scu)
        try:
            Lamel.objects.get(product_code=scu)
            return False
        except:
            return True

    def set_num_scu(self, scu, n):
        scu = str(scu)
        while len(scu) <= int(n):
            scu = '0' + scu
        return scu

    def get_max_scu(self):
        codes = Lamel.objects.all()
        max_scu = 0
        for code in codes:
            code = int(code.product_code)
            if code > max_scu:
                max_scu = code
        return max_scu

    def save(self, *args, **kwargs):
        if not self.product_code or not self.is_unique_scu(self.product_code):
            max_scu = int(self.get_max_scu())
            while True:
                new_scu = max_scu + 1
                if self.is_unique_scu(new_scu):
                    self.product_code = self.set_num_scu(new_scu, 4)
                    break

        # TODO: unique product_code

        if self.is_lamel and not self.weight_by_hand:
            m = 0.00075  # calculated empiric method
            vol = float(self.length) * float(self.lamel_width) * float(self.depth)
            self.weight = round((vol * m / 1000), 3)
        super(Lamel, self).save(*args, **kwargs)

    def get_price(self, request):
        return self.unit_price

    def get_rebate(self, x):
        some_str = self.discont_scheme.discont_scheme.split("\r\n")
        x = int(x)
        temp_discont = 0
        for i in some_str:
            discont = i.split(":")
            num = int(discont[0])  # get first element of tuple for get quantity in db
            if x >= num:
                temp_discont = int(discont[1])
            elif x <= num:
                return temp_discont
        return temp_discont

class LamelInventory(BaseInventory):
    product = models.ForeignKey(
        Lamel,
        on_delete=models.CASCADE,
        related_name='inventory_set',
    )

    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Available quantity in stock")
    )
