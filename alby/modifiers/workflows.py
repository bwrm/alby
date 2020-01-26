# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django_fsm import transition, RETURN_VALUE



class PayWhenTakeWorkflowMixin(object):
    """
    Workflow for marking the state as Ready for Self Colection, without delivery.
    all method added by Siarh
    """

    TRANSITION_TARGETS = {
        'ready_for_take': _("Ready for take"),
        'order_completed': _("Order completed"),
    }

    @transition(field='status', source='created', target='ready_for_take',
                custom=dict(admin=True, button_name=_("Prepare for taking")))
    def ready_for_take(self):
        """
        Put the parcel into the outgoing delivery.
        This method is invoked automatically
        """
        return 'ready_for_take'

    @transition(field='status', source='order_completed', target='ready_for_take',
                custom=dict(admin=True, button_name=_("Uncompletad")))
    def uncomplited(self):
        """
        Put the parcel into the outgoing delivery.
        This method is invoked automatically
        """
        return 'ready_for_take'

    @transition(field='status', source='ready_for_take', target='order_completed',
                custom=dict(admin=True, button_name=_("Mark as Completed")))
    def order_completed(self):
        """
        Signals that an Order can proceed directly, a payment when order will delivered.
        """
        return 'order_completed'
