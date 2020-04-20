from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import ProductList, SofaVariant
import os.path


@receiver(pre_save)
def save_scu(sender, instance=None, created=False, **kwargs):
    list_of_models = ('SofaVariant', 'Product', 'Commodity', 'Lamel', 'Fabric')
    if sender.__name__ in list_of_models: # this is the dynamic part you want
        a = instance.id
        saved_obj = ProductList.objects.create(product_model=sender.__name__)
        instance.product_code_id = saved_obj.id
