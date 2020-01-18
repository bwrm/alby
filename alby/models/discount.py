from django.db import models
from django.utils.translation import ugettext_lazy as _


class Discount(models.Model):
    discount_name = models.CharField(_("Discount name"), max_length=100)
    discont_scheme = models.TextField(_("Discount schema"), max_length=100, blank=True, help_text=_("Type discont scheme: first- quantity? second- rebate in %. Example: 10:25 - 10 -quantity 25%"))

    def __str__(self):
        return self.discount_name
