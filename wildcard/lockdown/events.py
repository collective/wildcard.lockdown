"""Event handlers."""
from ZPublisher.interfaces import IPubAfterTraversal
from plone import api
from wildcard.lockdown import CommitChecker
from wildcard.lockdown import logger
from wildcard.lockdown.interfaces import ILayer
from wildcard.lockdown.interfaces import ISettings
from zope.component import adapter
import traceback
import transaction


# meta types we're not going to bother checking
# for various reasons
_blacklisted_meta_types = {
    'Image',
    'File',
    'Filesystem Image',
    'Filesystem File',
    'Stylesheets Registry',
    'JavaScripts Registry',
    'DirectoryViewSurrogate',
    'KSS Registry',
    'Filesystem Directory View',
}


@adapter(IPubAfterTraversal)
def doomIt(event):
    """Doom the transaction if needed.

    The transaction will be doomed if lockdown is enabled and none of the
    activated commit conditions are met.

    See: https://zodb.readthedocs.io/en/latest/transactions.html#dooming-a-transaction
    """
    request = event.request
    published = request.PARENTS[0]
    mt = getattr(
        getattr(published, 'aq_base', None),
        'meta_type',
        getattr(published, 'meta_type', None))
    if (mt not in _blacklisted_meta_types) and ILayer.providedBy(request):
        if not _get_setting('enabled', False):
            # skip out of here first
            return

        status_message = _get_setting('status_message', None) or u''
        status_message = status_message.strip()
        if status_message and (not api.user.is_anonymous()):
            api.portal.show_message(
                status_message,
                request=request,
                type='warn')

        # let's check if this is valid now.
        activated = _get_setting('activated', set())
        try:
            checker = CommitChecker(request, activated)
            if checker.can_commit():
                return
        except Exception:
            # if there is any error, ignore and doom. better to be safe...
            logger.warn(
                'Error checking conditions, dooming the '
                'transaction: {}'.format(traceback.format_exc()))

        transaction.doom()


def _get_setting(name, default=api.portal.MISSING):
    return api.portal.get_registry_record(
        name=name,
        interface=ISettings,
        default=default)
