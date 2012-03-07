from wildcard.lockdown.interfaces import ISettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from wildcard.lockdown.testing import browserLogin
from wildcard.lockdown.testing import createObject
from plone.testing.z2 import Browser
import transaction
import unittest2 as unittest
from wildcard.lockdown.testing import Lockdown_FUNCTIONAL_TESTING


class TestLockdown(unittest.TestCase):

    layer = Lockdown_FUNCTIONAL_TESTING

    def setUp(self):
        from wildcard.lockdown import addCommitCondition
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        addCommitCondition("user-area",
            path="/users*",
            request_method="POST")
        folder = createObject(self.portal, 'Folder', 'users')
        createObject(folder, 'News Item', 'test1', title="Test 1")
        createObject(folder, 'News Item', 'test2', title="Test 2")
        createObject(self.portal, 'Document', 'testpage', title="Test page")

        transaction.commit()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        browserLogin(self.portal, self.browser)

    def activateCondition(self, name=None):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISettings)
        settings.enabled = True
        if name:
            settings.activated = set((name,))
        transaction.commit()

    def disableConditions(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISettings)
        settings.enabled = False
        settings.activated = set(())
        transaction.commit()

    def test_prevents_committing_to_database(self):
        self.activateCondition()
        baseurl = self.portal_url + '/testpage'
        newtitle = "EDITED TITLE"
        self.browser.open(baseurl)
        self.assertTrue(newtitle not in self.browser.contents)
        self.browser.open(baseurl + '/edit')
        self.browser.getControl(name='title').value = newtitle
        self.browser.getControl(name='form.button.save').click()
        self.assertTrue(newtitle not in self.browser.contents)

    def test_allows_writing_to_database(self):
        self.disableConditions()
        baseurl = self.portal_url + '/testpage'
        newtitle = "EDITED TITLE"
        self.browser.open(baseurl)
        self.assertTrue(newtitle not in self.browser.contents)
        self.browser.open(baseurl + '/edit')
        self.browser.getControl(name='title').value = newtitle
        self.browser.getControl(name='form.button.save').click()
        self.assertTrue(newtitle in self.browser.contents)

    def test_condition_should_allow_commit(self):
        self.activateCondition('user-area')
        baseurl = self.portal_url + '/users/test1'
        newtitle = "EDITED TITLE"
        self.browser.open(baseurl)
        self.assertTrue(newtitle not in self.browser.contents)
        self.browser.open(baseurl + '/edit')
        self.browser.getControl(name='title').value = newtitle
        self.browser.getControl(name='form.button.save').click()
        self.assertTrue(newtitle in self.browser.contents)
