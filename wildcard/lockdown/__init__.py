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
            self._site = getSite()
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

    def _checkPath(self, regex):
        path = self.req_path
        if regex.match(path):
            return True
        return False

    def _checkRequestMethod(self, method):
        req_meth = self.req.get('REQUEST_METHOD', '')
        return method == req_meth

    def _checkPortalType(self, pt):
        portal_type = getattr(
                getattr(self.req.PARENTS[0], 'aq_base', None),
                'portal_type',
                None)
        return portal_type == pt

    def _checkHost(self, regex):
        base1 = self.req.get('BASE1')
        _, base1 = base1.split('://', 1)
        host = base1.lower()
        if regex.match(host):
            return True
        return False

    def _checkCustom(self, func):
        return func(self.
            req)

    def checkCondition(self, condition):
        found = False
        for arg, value in condition.items():
            if arg in self._valid_args:
                if not self._valid_args[arg](self, value):
                    return False
                else:
                    found = True
        return found

    def canCommit(self):
        for name in self.conditions:
            if name in _conditions:
                condition = _conditions[name]
                # If one condition matches, we're good
                if self.checkCondition(condition):
                    return True
        return False

    _valid_args = {
        'path': _checkPath,
        'request_method': _checkRequestMethod,
        'portal_type': _checkPortalType,
        'host': _checkHost,
        'custom': _checkCustom}


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
