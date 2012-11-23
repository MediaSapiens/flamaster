from flask.ext.babel import lazy_gettext as _
from .base import BaseDelivery


class BasePerProduct(BaseDelivery):

    def check_availability(self, customer, order):
        pass


class PerProductDownload(BasePerProduct):
    name = _('E-ticket / Print@home')


class StandardDelivery(BasePerProduct):
    name = _('Standard')


class ExpressDelivery(BasePerProduct):
    name = _('Express')
