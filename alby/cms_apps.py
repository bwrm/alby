# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from cms.apphook_pool import apphook_pool
from cms.cms_menus import SoftRootCutter
from menus.menu_pool import menu_pool
from shop.cms_apphooks import CatalogListCMSApp, CatalogSearchCMSApp, OrderApp, PasswordResetApp
from alby.serializers.product import CustomizedProductSerializer
from alby.views import UpdateDataView

class CatalogListApp(CatalogListCMSApp):
    def get_urls(self, page=None, language=None, **kwargs):
        from shop.search.views import CMSPageCatalogWrapper
        from shop.views.catalog import AddToCartView, ProductRetrieveView
        from alby.serializers import CatalogSearchSerializer, RebateAddToCartSerializer, AddSofaToCartSerializer, UpdateDataSerialiser

        return [
            url(r'^$', CMSPageCatalogWrapper.as_view(
                search_serializer_class=CatalogSearchSerializer,
            )),
            url(r'^(?P<slug>[\w-]+)/add-to-cart', AddToCartView.as_view()),
            url(r'^(?P<slug>[\w-]+)/get-rebate', AddToCartView.as_view(
                serializer_class=RebateAddToCartSerializer,
            )),
            url(r'^(?P<slug>[\w-]+)/add-sofa-to-cart', AddToCartView.as_view(
                serializer_class=AddSofaToCartSerializer,
            )),
            url(r'^(?P<slug>[\w-]+)/update-small-data', UpdateDataView.as_view(
                serializer_class=UpdateDataSerialiser,
            )),
            url(r'^/divany/(?P<slug>[\w-]+)', ProductRetrieveView.as_view(
                use_modal_dialog=False,
                serializer_class=CustomizedProductSerializer,
            )),
            url(r'^(?P<slug>[\w-]+)', ProductRetrieveView.as_view(
                use_modal_dialog=False,
            )),
        ]


apphook_pool.register(CatalogListApp)


class CatalogSearchApp(CatalogSearchCMSApp):
    def get_urls(self, page=None, language=None, **kwargs):
        from shop.search.views import SearchView
        from alby.serializers import ProductSearchSerializer

        return [
            url(r'^', SearchView.as_view(
                serializer_class=ProductSearchSerializer,
            )),
        ]


apphook_pool.register(CatalogSearchApp)

apphook_pool.register(OrderApp)

apphook_pool.register(PasswordResetApp)


def _deregister_menu_pool_modifier(Modifier):
    index = None
    for k, modifier_class in enumerate(menu_pool.modifiers):
        if issubclass(modifier_class, Modifier):
            index = k
    if index is not None:
        # intentionally only modifying the list
        menu_pool.modifiers.pop(index)


_deregister_menu_pool_modifier(SoftRootCutter)
