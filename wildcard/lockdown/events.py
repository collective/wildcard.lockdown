from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.component import adapter
import transaction
from ZPublisher.interfaces import IPubAfterTraversal
from wildcard.lockdown import CommitChecker
from wildcard.lockdown.interfaces import ILayer
from wildcard.lockdown.interfaces import ISettings
from wildcard.lockdown import logger
import traceback


# meta types we're not going to bother checking
# for various reasons
_blacklisted_meta_types = ('Image', 'File', 'Filesystem Image',
    'Filesystem File', 'Stylesheets Registry', 'JavaScripts Registry',
    'DirectoryViewSurrogate', 'KSS Registry', 'Filesystem Directory View')


@adapter(IPubAfterTraversal)
def doomIt(event):
    request = event.request
    published = request.PARENTS[0]
    mt = getattr(
            getattr(published, 'aq_base', None),
            'meta_type',
            getattr(published, 'meta_type', None))
    if mt not in _blacklisted_meta_types and ILayer.providedBy(request):
        # print 'checking', repr(published),
        # print getattr(published, 'meta_type', None)
        try:
            registry = getUtility(IRegistry)
        except KeyError:
            logger.warn("settings not installed")
            return  # settings not installed
        try:
            settings = registry.forInterface(ISettings)
        except KeyError:
            logger.warn("settings not installed")
            return  # settings not registered

        if not settings.enabled:
            # skip out of here first
            return

        # let's check if this is valid now.
        try:
            checker = CommitChecker(request, settings.activated)
            if checker.can_commit():
                return
        except Exception:
            # if there is any error, ignore and doom
            # better to be safe..
            logger.warn("Error checking conditions, "
                        "dooming the tranaction: %s" %
                            traceback.format_exc())
        transaction.doom()
