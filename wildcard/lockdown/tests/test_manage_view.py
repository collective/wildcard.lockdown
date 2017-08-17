import unittest
from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles
from wildcard.lockdown.testing import Lockdown_INTEGRATION_TESTING
from AccessControl import Unauthorized
from plone import api
import json
from ..interfaces import ISettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


class TestManageView(unittest.TestCase):

    layer = Lockdown_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self._settings = registry.forInterface(ISettings)

    def test_view_is_protected(self):
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@manage-lockdown')

    def test_can_get_options(self):
        current_options = {
            'enabled': False,
            'activated': {u'All POST'},
            'status_message': None
        }
        self._set_options(**current_options)

        options_from_view = self._render_view()
        self.assertDictEqual(self._adjust_dict_to_json(current_options), options_from_view)

    def test_can_set_options(self):
        old_options = {
            'enabled': False,
            'activated': {u'All POST'},
            'status_message': u'Test status message.'
        }
        self._set_options(**old_options)

        new_options = {
            'enabled': True,
            'activated': [u'Logged in user'],  # JSON does not have sets.
            'status_message': u'Other status message',
        }

        # Simulate a POST with the new options.
        for (k, v) in new_options.iteritems():
            self.request.form[k] = v
        self.request['REQUEST_METHOD'] = 'POST'
        result = self._render_view()
        self.assertEqual(result, u'OK')

        self.assertDictEqual(
            self._adjust_dict_to_json(self._get_options_as_dict()),
            new_options)

    def test_omited_options_remains_unchanged(self):
        old_options = {
            'enabled': False,
            'activated': {u'All POST'},
            'status_message': u'Test status message.'
        }
        self._set_options(**old_options)

        new_options = {
            'activated': [u'Logged in user'],  # JSON does not have sets.
        }

        # Simulate a POST with the new options.
        for (k, v) in new_options.iteritems():
            self.request.form[k] = v
        self.request['REQUEST_METHOD'] = 'POST'
        result = self._render_view()
        self.assertEqual(result, u'OK')

        current_options = self._adjust_dict_to_json(self._get_options_as_dict())
        for (k, v) in current_options.iteritems():
            if k in new_options:
                self.assertEqual(new_options[k], current_options[k])
            else:
                self.assertEqual(old_options[k], current_options[k])

    def _render_view(self):
        view = api.content.get_view(
            name='manage-lockdown',
            context=self.portal,
            request=self.request)
        result = view()
        return json.loads(result)

    def _adjust_dict_to_json(self, d):
        return {
            k: (list(v) if isinstance(v, set) else v)
            for (k, v)
            in d.iteritems()
        }

    def _set_options(self, **kwargs):
        for (k, v) in kwargs.iteritems():
            setattr(self._settings, k, v)

    def _get_options_as_dict(self):
        return {k: getattr(self._settings, k) for k in ISettings}


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
