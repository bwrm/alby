# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from cms.sitemaps import CMSSitemap
from alby.sitemap import ProductSitemap
from alby.settings import prefix_default_language as is_prefix

# from phone_verify.api import VerificationViewSet


sitemaps = {'cmspages': CMSSitemap,
            'products': ProductSitemap}


def render_robots(request):
    permission = 'noindex' in settings.ROBOTS_META_TAGS and 'Disallow' or 'Allow'
    return HttpResponse(''
                        'User-Agent: *\n'
                        '%s: /\n'
                        'Disallow: /personal-pages/\n'
                        'Disallow: /cart/\n'
                        'Disallow: /register-customer/\n'
                        'Disallow: /request-password-reset/\n'
                        'Disallow: /search/\n'
                        'Sitemap: http://alby.by/sitemap.xml\n'
                        '' % permission, content_type='text/plain')

i18n_urls = (
    url(r'^admin/', admin.site.urls),
    url(r'^', include('cms.urls')),
)
urlpatterns = [
    url(r'^robots\.txt$', render_robots),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    url(r'^shop/', include('shop.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    # url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    # url(r'^', include('phone_verify.urls'))
]

if settings.USE_I18N:
    urlpatterns.extend(i18n_patterns(*i18n_urls, prefix_default_language=is_prefix))
else:
    urlpatterns.extend(i18n_urls)
urlpatterns.extend(
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
