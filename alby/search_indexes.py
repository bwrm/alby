# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from haystack import indexes
from shop.search.indexes import ProductIndex as ProductIndexBase
from alby.models import  Commodity, Lamel


class ProductIndex(ProductIndexBase):
    catalog_media = indexes.CharField(stored=True, indexed=False, null=True)
    search_media = indexes.CharField(stored=True, indexed=False, null=True)
    caption = indexes.CharField(
        stored=True, indexed=False, null=True, model_attr='caption')

    def prepare_catalog_media(self, product):
        return self.render_html('catalog', product, 'media')

    def prepare_search_media(self, product):
        return self.render_html('search', product, 'media')


myshop_search_index_classes = []


# class CommodityIndex(ProductIndex, indexes.Indexable):
#     def get_model(self):
#         return Commodity

class LamelIndex(ProductIndex, indexes.Indexable):
    def get_model(self):
        return Lamel


# myshop_search_index_classes.append(CommodityIndex)
myshop_search_index_classes.append(LamelIndex)

