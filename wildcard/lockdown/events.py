from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.component import adapter
import transaction
from ZPublisher.interfaces import IPubAfterTraversal
from wildcard.lockdown import checkCondition
from wildcard.lockdown.interfaces import ILayer
from wildcard.lockdown.interfaces import ISettings
from wildcard.lockdown import logger


# meta types we're not going to bother checking
# for various reasons
_blacklisted_meta_types = ('Image', 'File', 'Filesystem Image')


@adapter(IPubAfterTraversal)
def doomIt(event):
    request = event.request
    mt = getattr(
            getattr(request.PARENTS[0], 'aq_base', None),
            'meta_type',
            None)
    if mt not in _blacklisted_meta_types and ILayer.providedBy(request):
        try:
            registry = getUtility(IRegistry)
        except KeyError:
            return  # settings not installed
        try:
            settings = registry.forInterface(ISettings)
        except KeyError:
            return  # settings not registered

        if not settings.enabled:
            # skip out of here first
            return

        # let's check if this is valid now.
        try:
            for condition in settings.activated:
                if checkCondition(condition, request):
                    return
        except Exception:
            # if there is any error, ignore and doom
            # better to be safe..
            logger.warn("Error checking '%s', dooming the tranaction" %
                condition)
        transaction.doom()
