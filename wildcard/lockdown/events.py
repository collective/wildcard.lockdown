from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.component import adapter
import transaction
from ZPublisher.interfaces import IPubSuccess
from wildcard.lockdown import checkCondition
from wildcard.lockdown.interfaces import ILayer
from wildcard.lockdown.interfaces import ISettings


@adapter(IPubSuccess)
def doomIt(event):
    request = event.request
    if ILayer.providedBy(request):
        import pdb; pdb.set_trace()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISettings)
        if not settings.enabled:
            return
        for condition in settings.activated:
            if checkCondition(condition, request):
                return
        transaction.doom()
