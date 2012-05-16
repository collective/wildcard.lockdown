from Products.CMFCore.utils import getToolByName
from zope.i18nmessageid import MessageFactory
import fnmatch
import re
import logging
from zope.app.component.hooks import getSite

_ = MessageFactory('collective.routes')
logger = logging.getLogger('wildcard.lockdown')

_globbed_params = ('path', 'host')
_conditions = {}


def initialize(context):
    pass


class CommitChecker(object):

    def __init__(self, req, conditions):
        self.req = req
        self.conditions = conditions

    @property
    def site(self):
        if not hasattr(self, '_site'):
            urltool = getToolByName(self.req.PARENTS[0], 'portal_url', None)
            if urltool is None:
                self._site = getSite()
            else:
                self._site = urltool.getPortalObject()
        return self._site

    @property
    def req_path(self):
        if not hasattr(self, '_req_path'):
            fullpath = self.req.physicalPathFromURL(
                self.req.get('ACTUAL_URL', ''))
            site_path = self.site.getPhysicalPath()
            path = fullpath[len(site_path):]
            self._req_path = '/' + '/'.join(path).lstrip('/')
        return self._req_path

    def _check_path(self, regex):
        path = self.req_path
        if regex.match(path):
            return True
        return False

    def _check_request_method(self, method):
        req_meth = self.req.get('REQUEST_METHOD', '')
        return method.lower() == req_meth.lower()

    def _check_portal_type(self, pt):
        item = self.req.PARENTS[0]
        portal_type = getattr(
                getattr(item, 'aq_base', item),
                'portal_type',
                None)
        return portal_type == pt

    def _check_host(self, regex):
        base1 = self.req.get('BASE1')
        _, base1 = base1.split('://', 1)
        host = base1.lower()
        if regex.match(host):
            return True
        return False

    def _check_custom(self, func):
        return func(self.req)

    def _check_logged_in(self, _):
        mt = getToolByName(self.site, 'portal_membership', None)
        if not mt:
            return False
        return not mt.isAnonymousUser()

    def check_condition(self, condition):
        found = False
        for arg, value in condition.items():
            if arg in self._valid_args:
                if not self._valid_args[arg](self, value):
                    return False
                else:
                    found = True
        return found

    def can_commit(self):
        for name in self.conditions:
            if name in _conditions:
                condition = _conditions[name]
                # If one condition matches, we're good
                if self.check_condition(condition):
                    return True
        return False

    _valid_args = {
        'path': _check_path,
        'request_method': _check_request_method,
        'portal_type': _check_portal_type,
        'host': _check_host,
        'custom': _check_custom,
        'logged_in': _check_logged_in}


def addCommitCondition(name, **kwargs):
    for globbed_name in _globbed_params:
        if globbed_name in kwargs:
            regex = fnmatch.translate(kwargs[globbed_name])
            kwargs[globbed_name] = re.compile(regex)
    _conditions[name] = kwargs


def getConditionNames():
    return _conditions.keys()


addCommitCondition("Allow Lockdown Settings Editing",
    path="/@@lockdown-settings",
    request_method='POST',
    portal_type="Plone Site")
addCommitCondition("Logged in user", logged_in=True)
addCommitCondition("All POST", request_method='POST')
addCommitCondition("Only localhost", host='localhost:*')
addCommitCondition("Only 127.0.0.1", host='127.0.0.1:*')
