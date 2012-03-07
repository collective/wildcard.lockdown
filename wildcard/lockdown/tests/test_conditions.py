import unittest2 as unittest
from wildcard.lockdown.testing import Lockdown_FUNCTIONAL_TESTING
from wildcard.lockdown import CommitChecker
from wildcard.lockdown import addCommitCondition


class FakePT(object):
    def __init__(self, pt):
        self.portal_type = pt


class TestConditionTypes(unittest.TestCase):

    layer = Lockdown_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

    def test_path_condition_success(self):
        addCommitCondition("path-condition",
            path="/foo/bar")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo/bar')
        checker = CommitChecker(self.request, ('path-condition',))
        self.assertTrue(checker.can_commit())

    def test_path_condition_sucess_with_wildcard(self):
        addCommitCondition("path-condition",
            path="/foo*")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo/bar')
        checker = CommitChecker(self.request, ('path-condition',))
        self.assertTrue(checker.can_commit())

    def test_path_condition_fail(self):
        addCommitCondition("path-condition",
            path="/foo/bar")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo/bars')
        checker = CommitChecker(self.request, ('path-condition',))
        self.assertTrue(not checker.can_commit())

    def test_path_condition_fail_with_wildcard(self):
        addCommitCondition("path-condition",
            path="/foo*")
        self.request.set('ACTUAL_URL', self.portal_url + '/fob/oar')
        checker = CommitChecker(self.request, ('path-condition',))
        self.assertTrue(not checker.can_commit())

    def test_request_condition_success(self):
        addCommitCondition("request-method-condition",
            request_method="POST")
        self.request.set('REQUEST_METHOD', 'POST')
        checker = CommitChecker(self.request, ('request-method-condition',))
        self.assertTrue(checker.can_commit())

    def test_request_condition_success_case_insensitive(self):
        addCommitCondition("request-method-condition",
            request_method="put")
        self.request.set('REQUEST_METHOD', 'PUT')
        checker = CommitChecker(self.request, ('request-method-condition',))
        self.assertTrue(checker.can_commit())

    def test_request_condition_fail(self):
        addCommitCondition("request-method-condition",
            request_method="POST")
        self.request.set('REQUEST_METHOD', 'GET')
        checker = CommitChecker(self.request, ('request-method-condition',))
        self.assertTrue(not checker.can_commit())

    def test_host_condition_success(self):
        addCommitCondition("host-condition",
            host="www.foobar.com")
        self.request.set('BASE1', 'http://www.foobar.com')
        checker = CommitChecker(self.request, ('host-condition',))
        self.assertTrue(checker.can_commit())

    def test_host_condition_plus_port_success(self):
        addCommitCondition("host-condition",
            host="www.foobar.com:8080")
        self.request.set('BASE1', 'https://www.foobar.com:8080')
        checker = CommitChecker(self.request, ('host-condition',))
        self.assertTrue(checker.can_commit())

    def test_host_condition_wildcard_success(self):
        addCommitCondition("host-condition",
            host="*.bar.com")
        self.request.set('BASE1', 'http://foo.bar.com')
        checker = CommitChecker(self.request, ('host-condition',))
        self.assertTrue(checker.can_commit())

    def test_host_condition_fail(self):
        addCommitCondition("host-condition",
            host="www.foobar.com")
        self.request.set('BASE1', 'http://www.foboar.com')
        checker = CommitChecker(self.request, ('host-condition',))
        self.assertTrue(not checker.can_commit())

    def test_host_condition_wildcard_fail(self):
        addCommitCondition("host-condition",
            host="*.bar.com")
        self.request.set('BASE1', 'http://fob.oar.com')
        checker = CommitChecker(self.request, ('host-condition',))
        self.assertTrue(not checker.can_commit())

    def test_portal_type_condition_success(self):
        addCommitCondition("pt-condition",
            portal_type="foobar")
        self.request.set('PARENTS', [FakePT('foobar')])
        checker = CommitChecker(self.request, ('pt-condition',))
        self.assertTrue(checker.can_commit())

    def test_portal_type_condition_fail(self):
        addCommitCondition("pt-condition",
            portal_type="foobar")
        self.request.set('PARENTS', [FakePT('foboar')])
        checker = CommitChecker(self.request, ('pt-condition',))
        self.assertTrue(not checker.can_commit())

    def test_custom_condition_success(self):
        def custom(req):
            return True
        addCommitCondition("custom-condition",
            custom=custom)
        checker = CommitChecker(self.request, ('custom-condition',))
        self.assertTrue(checker.can_commit())

    def test_custom_condition_fail(self):
        def custom(req):
            return False
        addCommitCondition("custom-condition",
            custom=custom)
        checker = CommitChecker(self.request, ('custom-condition',))
        self.assertTrue(not checker.can_commit())


class TestCompoundConditions(unittest.TestCase):
    """
    Multiple criteria for one condition
    """

    layer = Lockdown_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

    def test_all_criteria_must_be_met_success(self):
        addCommitCondition("condition",
            path="/foo/bar",
            request_method="POST",
            domain="www.foobar.com")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo/bar')
        self.request.set('REQUEST_METHOD', 'POST')
        self.request.set('BASE1', 'http://www.foobar.com')
        checker = CommitChecker(self.request, ('condition',))
        self.assertTrue(checker.can_commit())

    def test_one_criteria_not_met(self):
        addCommitCondition("condition",
            path="/foo/bar",
            request_method="POST",
            domain="www.foobar.com")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo')
        self.request.set('REQUEST_METHOD', 'POST')
        self.request.set('BASE1', 'http://www.foobar.com')
        checker = CommitChecker(self.request, ('condition',))
        self.assertTrue(not checker.can_commit())

    def test_all_criteria_not_met(self):
        addCommitCondition("condition",
            path="/foo/bar",
            request_method="POST",
            domain="www.foobar.com")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo')
        self.request.set('REQUEST_METHOD', 'GET')
        self.request.set('BASE1', 'http://www.foboar.com')
        checker = CommitChecker(self.request, ('condition',))
        self.assertTrue(not checker.can_commit())

    def test_multiple_conditions_all_success(self):
        addCommitCondition("path", path="/foo/bar")
        addCommitCondition("method", request_method="POST",
            domain="www.foobar.com")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo/bar')
        self.request.set('REQUEST_METHOD', 'POST')
        self.request.set('BASE1', 'http://www.foobar.com')
        checker = CommitChecker(self.request, ('path', 'method'))
        self.assertTrue(checker.can_commit())

    def test_multiple_conditions_one_success(self):
        addCommitCondition("path", path="/foo/bar")
        addCommitCondition("method", request_method="POST",
            domain="www.foobar.com")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo/bar')
        self.request.set('REQUEST_METHOD', 'GET')
        self.request.set('BASE1', 'http://www.foobar.com')
        checker = CommitChecker(self.request, ('path', 'method'))
        self.assertTrue(checker.can_commit())

    def test_multiple_conditions_all_fail(self):
        addCommitCondition("path", path="/foo/bar")
        addCommitCondition("method", request_method="POST",
            domain="www.foobar.com")
        self.request.set('ACTUAL_URL', self.portal_url + '/foo')
        self.request.set('REQUEST_METHOD', 'GET')
        self.request.set('BASE1', 'http://www.foboar.com')
        checker = CommitChecker(self.request, ('path', 'method'))
        self.assertTrue(not checker.can_commit())
