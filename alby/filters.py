# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet

from djng.forms import NgModelFormMixin
from djng.styling.bootstrap3.forms import Bootstrap3Form

from shop.filters import ModelChoiceFilter

from alby.models import Product


class FilterForm(NgModelFormMixin, Bootstrap3Form):
    scope_prefix = 'filters'


