# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.forms import widgets, Media
from django.forms.utils import ErrorDict
from django.utils.translation import ugettext_lazy as _
from djng.forms import fields
from sass_processor.processor import sass_processor
from shop.forms.base import DialogForm, DialogModelForm, UniqueEmailValidationMixin
from shop.forms.widgets import CheckboxInput, RadioSelect, Select
from shop.models.address import ShippingAddressModel, BillingAddressModel
from shop.models.customer import CustomerModel
from shop.modifiers.pool import cart_modifiers_pool
from shop.forms.checkout import AddressForm, ShippingAddressForm as BaseShippingAddressForm
from shop.forms.checkout import ShippingMethodForm as BaseShippingMethodForm
from shop.forms.checkout import PaymentMethodForm as BasePaymentMethodForm
from shop.forms.checkout import CustomerForm as BaseCustomerForm
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

class CustomerForm(DialogModelForm):
    scope_prefix = 'customer'
    legend = _("Customer's Details")
    email = fields.EmailField(label=_("Email address"))
    phone = PhoneNumberField()
    first_name = fields.CharField(label=_("First Name"))
    #last_name = fields.CharField(label=_("Last Name"))
    field_order = ['first_name','email', 'phone']

    class Meta:
        model = CustomerModel
        exclude = ['user', 'recognized', 'number', 'last_access', 'last_name']
        custom_fields = ['email','phone', 'first_name']

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        initial = dict(initial) if initial else {}
        assert instance is not None
        initial.update(dict((f, getattr(instance, f)) for f in self.Meta.custom_fields))
        super(CustomerForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)
        self.fields['email'].required = False
        self.fields['phone'].required = True

    @property
    def media(self):
        return Media(css={'all': [sass_processor('shop/css/customer.scss')]})

    def save(self, commit=True):
        for f in self.Meta.custom_fields:
            setattr(self.instance, f, self.cleaned_data[f])
        return super(CustomerForm, self).save(commit)

    @classmethod
    def form_factory(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.customer)
        if customer_form.is_valid():
            customer_form.instance.recognize_as_registered(request, commit=False)
            customer_form.save()
        return customer_form


class GuestForm(DialogModelForm):
    scope_prefix = 'guest'
    form_name = 'customer_form'  # Override form name to reuse template `customer-form.html`
    legend = _("Customer's Phone number")

    phone = PhoneNumberField()

    class Meta:
        model = get_user_model()  # since we only use the email field, use the User model directly
        fields = ['phone']

    def __init__(self, initial=None, instance=None, *args, **kwargs):
        if isinstance(instance, CustomerModel):
            instance = instance.user
        super(GuestForm, self).__init__(initial=initial, instance=instance, *args, **kwargs)

    @classmethod
    def form_factory(cls, request, data, cart):
        customer_form = cls(data=data, instance=request.customer.user)
        if customer_form.is_valid():
            request.customer.recognize_as_guest(request, commit=False)
            customer_form.save()
        return customer_form


class ShippingAddressForm(BaseShippingAddressForm):
    scope_prefix = 'shipping_address'
    legend = _("Shipping Address")

    class Meta(AddressForm.Meta):
        model = ShippingAddressModel
        exclude = ['name','country', 'address2', 'customer', 'priority']
        # widgets = {
        #     'country': Select(attrs={'ng-change': 'updateSiblingAddress()'}),
        # }

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.fields['address1'].required = False
        self.fields['zip_code'].required = False
        self.fields['city'].required = False


class PaymentMethodForm(DialogForm):

    scope_prefix = 'payment_method'

    payment_modifier = fields.ChoiceField(
        label=_("Payment Method"),
        widget=RadioSelect(attrs={'ng-change': 'updateMethod()'}),
    )

    def __init__(self, *args, **kwargs):
        choices = [m.get_choice() for m in cart_modifiers_pool.get_payment_modifiers()]
        self.base_fields['payment_modifier'].choices = choices
        if len(choices) == 1:
            # if there is only one shipping method available, always set it as default
            try:
                kwargs['initial']['payment_modifier'] = choices[0][0]
            except KeyError:
                pass
        super(PaymentMethodForm, self).__init__(*args, **kwargs)

    def has_choices(self):
        return len(self.base_fields['payment_modifier'].choices) > 0

    @classmethod
    def form_factory(cls, request, data, cart):
        cart.update(request)
        active_mod = data['payment_modifier'] if data['payment_modifier'] is not None else cart.extra['payment_modifier']
        current_payment_cart_modifier = cart_modifiers_pool.get_active_payment_modifier(active_mod)
        payment_method_form = cls(data=data, cart=cart)
        city = cart.shipping_address.city
        try:
            if current_payment_cart_modifier.is_disabled(cart):
                payment_method_form.add_error('payment_modifier', _('Select a valid Payment method. Is not one of the available choices.'))
        except:
            pass
        if payment_method_form.is_valid():
            payment_data = data.get('payment_data') or {}
            cart.extra.update(payment_method_form.cleaned_data, payment_extra_data=payment_data)
        return payment_method_form

class ShippingMethodForm(BaseShippingMethodForm):

    def __init__(self, *args, **kwargs):
        choices = [m.get_choice() for m in cart_modifiers_pool.get_shipping_modifiers()
                   if not m.is_disabled(kwargs['cart'])]
        self.base_fields['shipping_modifier'].choices = choices
        super(ShippingMethodForm, self).__init__(*args, **kwargs)
