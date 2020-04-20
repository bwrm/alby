from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework.generics import RetrieveAPIView
from alby.models import ProductList
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST
from django.shortcuts import get_object_or_404



class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class UpdateDataView(RetrieveAPIView):
    product_model = ProductList

    def get_context(self, request, **kwargs):
        code = self.request.data.get('product_code')
        product = self.product_model.objects.get(product_code=code)
        product = product.fabric_set.get(product_code=product.id)
        # product = get_object_or_404(queryset)
        # product = product.product_code
        return {'product': product, 'request': request}

    def post(self, request, *args, **kwargs):
        context = self.get_context(request, **kwargs)
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer.data, status=HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

