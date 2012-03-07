from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

_records_to_delete = (
    'wildcard.lockdown.interfaces.ISettings.enabled',
    'wildcard.lockdown.interfaces.ISettings.activated')


def uninstall(context, reinstall=False):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-wildcard.lockdown:uninstall')
    if not reinstall:
        registry = getUtility(IRegistry)
        for record in _records_to_delete:
            del registry.records[record]
