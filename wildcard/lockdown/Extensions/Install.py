"""Provide the `uninstall` function."""
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from wildcard.lockdown.interfaces import ISettings


def uninstall(context, reinstall=False):
    """Uninstall the add-on."""
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-wildcard.lockdown:uninstall')
    if not reinstall:
        registry = getUtility(IRegistry)
        records = registry.records
        to_delete = [
            ISettings.__identifier__ + '.' + name
            for name
            in ISettings]
        to_delete = [r for r in to_delete if r in records]
        for record in to_delete:
            del records[record]
