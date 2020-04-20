from shop.serializers.bases import ProductSerializer
from alby.models import SofaModel


class CustomizedProductSerializer(ProductSerializer):
    class Meta:
        model = SofaModel
        fields = ['id', 'product_name', 'product_url', 'product_model', 'price', 'media']
