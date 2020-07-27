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
from shop.money.fields import MoneyField
from shop.models.product import BaseProduct, BaseProductManager, CMSPageReferenceMixin
from shop.models.inventory import BaseInventory, AvailableProductMixin
from alby.models.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.defaults.delivery import Delivery
from shop.models.defaults.delivery_item import DeliveryItem
from shop.models.defaults.mapping import ProductPage, ProductImage
from alby.models.address import BillingAddress, ShippingAddress
from alby.models.customer import Customer
from alby.models.discount import Discount
from shop.money import Money
from filer.fields import image

__all__ = ['Cart', 'CartItem', 'BillingAddress', 'ShippingAddress', 'Customer', ]

class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass

class ProductManager(BaseProductManager, TranslatableManager):
    queryset_class = ProductQuerySet

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db)
        return qs.prefetch_related('translations')

class ProductList(models.Model):
    product_code = models.CharField(
        _("Product model"),
        max_length=255,
        unique=True,
    )
    product_model = models.CharField(
        _("Product model"),
        max_length=255,
        blank=True,
    )
    def is_unique_scu(self, scu):
        scu = str(scu)
        return ProductList.objects.filter(product_code=scu).count() == 0

    def set_num_scu(self, scu, n):
        scu = str(scu)
        while len(scu) <= int(n):
            scu = '0' + scu
        return scu

    def get_max_scu(self):
        max_scu = ProductList.objects.aggregate(models.Max('product_code'))
        try:
            return int(max_scu['product_code__max'])
        except:
            return 1

    def save(self, *args, **kwargs):
        if not self.product_code:
            max_scu = self.get_max_scu()
            while True:
                new_scu = max_scu + 1
                if self.is_unique_scu(new_scu):
                    self.product_code = self.set_num_scu(new_scu, 4)
                    break
        super(ProductList, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_code


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
    product_title = models.CharField(
        _("Product Title (for SEO)"),
        max_length=255,
        blank=True,
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
        blank=True
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
    ),
    description=HTMLField(
        verbose_name=_("Description"),
        configuration='CKEDITOR_SETTINGS_DESCRIPTION',
        blank=True,
        help_text=_(
            "Full description used in the catalog's detail view of Smart Cards."),
    ),

    class Meta:
        unique_together = [('language_code', 'master')]


class Commodity(AvailableProductMixin, Product, TranslatableModelMixin):
    """
    This Commodity model inherits from polymorphic Product, and therefore has to be redefined.
    """
    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )
    product_code = models.ForeignKey(
        ProductList,
        on_delete=models.CASCADE,
    )
    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
        caption=HTMLField(
            verbose_name=_("Caption"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
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
    product_code = models.ForeignKey(
        ProductList,
        on_delete=models.CASCADE,
        blank=True,
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
        default=0,
        blank=True,
    )

    depth = models.CharField(
        _("Lamel's depth"),
        max_length=25,
        default=8,
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
    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
        caption=HTMLField(
            verbose_name=_("Caption"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
    )

    discont_scheme = models.ForeignKey(Discount, blank=True, null=True, on_delete=models.CASCADE)


    default_manager = ProductManager()

    class Meta:
        verbose_name = _("Lamel")
        verbose_name_plural = _("Lamels")

    def save(self, *args, **kwargs):
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

class Fabric(Product):

    fabric_name = models.CharField(
        _("Fabric name"),
        max_length=150,
        blank=True,
    )
    # common product fields
    unit_price = MoneyField(
        _("Price per meter"),
        decimal_places=2,
        help_text=_("Net price for this product by meter"),
    )
    # product properties
    FABRIC_TYPE = [
        ('leath','leather'),
        ('velv', 'velvet'),
        ('wool','wool'),
    ]
    fabric_type = models.CharField(
        _("Fabric type"),
        choices=FABRIC_TYPE,
        max_length=15,
    )

    product_code = models.ForeignKey(
        ProductList,
        on_delete=models.CASCADE,
        blank=True,
    )
    composition = models.CharField(
        _("Comosition of fabric"),
        max_length=255,
        unique=False,
    )
    care = models.CharField(
        _("Recommended wash care"),
        max_length=255,
        unique=False,
    )
    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
        caption=HTMLField(
            verbose_name=_("Caption"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
    )

    default_manager = ProductManager()

    class Meta:
        verbose_name = _("Fabric")
        verbose_name_plural = _("Fabrics")

    def get_price(self, request):
        return self.unit_price

class SofaModel(Product):
    sofa_type = models.CharField(
        _("Sofa Type"),
        choices=[(t, t) for t in (_('Straight'), _('Corner'), _('2 seat'), _('3 seat'), _('Sofabed'), _('Chair'))],
        max_length=9,
    )
    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
        caption=HTMLField(
            verbose_name=_("Caption"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            blank=True,
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
    )
    # other fields to map the specification sheet

    default_manager = ProductManager()

    lookup_fields = ('product_name__icontains',)

    def get_price(self, request):
        aggregate = self.variants.aggregate(models.Min('unit_price'))
        return Money(aggregate['unit_price__min'])

    def is_in_cart(self, cart, watched=False, **kwargs):
        try:
            product_code = kwargs['product_code']
        except KeyError:
            return
        cart_item_qs = CartItem.objects.filter(cart=cart, product=self)
        for cart_item in cart_item_qs:
            if cart_item.product_code == product_code:
                return cart_item

    def get_product_variant(self, **kwargs):
        try:
            product_code = kwargs.get('product_code')
            #added new model for the whole product list
            id_var = ProductList.objects.get(product_code=product_code).id
            return self.variants.get(product_code=id_var)
        except SofaVariant.DoesNotExist as e:
            raise SofaModel.DoesNotExist(e)


class SofaVariant(models.Model):

    class Meta:
        ordering = ('unit_price',)

    product_model = models.ForeignKey(
        SofaModel,
        related_name='variants',
        on_delete=models.CASCADE,
    )
    product_code = models.ForeignKey(
        ProductList,
        on_delete=models.CASCADE,
        blank=True,
    )
    images = models.ManyToManyField(
        'filer.Image',
        through='VariantImage',
        )

    unit_price = MoneyField(_("Unit price"), blank=True)

    fabric = models.ForeignKey(
        Fabric,
        on_delete=models.CASCADE,
        blank=True,
    )
    def get_availability(self, request, **kwargs):
        return True
    def __str__(self):
        return self.fabric.fabric_name

    def delete(self, using=None, keep_parents=False):
        ProductList.objects.filter(product_code=self.product_code).delete()
        super(SofaVariant, self).delete()

class VariantImage(models.Model):
    image = image.FilerImageField(on_delete=models.CASCADE)
    product = models.ForeignKey(
        SofaVariant,
        on_delete=models.CASCADE,
        blank=True,
    )
    order = models.SmallIntegerField(default=0)
    class Meta:
        abstract = False
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['order']

