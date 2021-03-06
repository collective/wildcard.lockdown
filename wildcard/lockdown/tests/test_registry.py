from zope.interface import alsoProvides

import unittest

from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.registry import Registry
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from wildcard.lockdown.interfaces import ISettings
from wildcard.lockdown.testing import Lockdown_INTEGRATION_TESTING
from wildcard.lockdown.interfaces import ILayer

BASE_REGISTRY = 'wildcard.lockdown.interfaces.ISettings.%s'


class RegistryTest(unittest.TestCase):

    layer = Lockdown_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # set up settings registry
        self.registry = Registry()
        self.registry.registerInterface(ISettings)

        request = self.portal.REQUEST
        alsoProvides(request, ILayer)

    def test_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='lockdown-settings')
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@lockdown-settings')

    def test_action_in_controlpanel(self):
        cp = getToolByName(self.portal, 'portal_controlpanel')
        actions = [a.getAction(self)['id'] for a in cp.listActions()]
        self.failUnless('lockdown' in actions)

    def test_activated_record(self):
        record = self.registry.records[
            BASE_REGISTRY % 'activated']
        self.failUnless('activated' in ISettings)
        self.assertEquals(record.value, set([]))


class RegistryUninstallTest(unittest.TestCase):

    layer = Lockdown_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = getUtility(IRegistry)
        # uninstall the package
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=['wildcard.lockdown'])

    def test_records_removed_from_registry(self):
        records = [
            'wildcard.lockdown.interfaces.ISettings.activated',
            'wildcard.lockdown.interfaces.ISettings.enabled'
            ]
        for r in records:
            self.failIf(r in self.registry.records,
                        '%s record still in configuration registry' % r)

    def test_action_no_longer_in_controlpanel(self):
        cp = getToolByName(self.portal, 'portal_controlpanel')
        actions = [a.getAction(self)['id'] for a in cp.listActions()]
        self.failUnless('lockdown' not in actions)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
