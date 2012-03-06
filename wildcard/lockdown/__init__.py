from zope.i18nmessageid import MessageFactory
import fnmatch
import re
import logging

_ = MessageFactory('collective.routes')
logger = logging.getLogger('wildcard.lockdown')


def initialize(context):
    pass


def _checkPath(regex, req):
    url = req.get('ACTUAL_URL', '')
    if regex.match(url):
        return True
    return False


def _checkRequestMethod(method, req):
    req_meth = req.get('REQUEST_METHOD', '')
    return method == req_meth


def _checkPortalType(pt, req):
    portal_type = getattr(
            getattr(req.PARENTS[0], 'aq_base', None),
            'portal_type',
            None)
    return portal_type == pt


def _checkDomain(regex, req):
    req_domain = req.get('Host')
    if regex.match(req_domain):
        return True
    return False


def _checkCustom(func, req):
    return func(req)


_valid_args = {
    'path': _checkPath,
    'request_method': _checkRequestMethod,
    'portal_type': _checkPortalType,
    'domain': _checkDomain,
    'custom': _checkCustom}

_globbed_params = ('path', 'domain')
_conditions = {}


def addCommitCondition(name, **kwargs):
    for globbed_name in _globbed_params:
        if globbed_name in kwargs:
            regex = fnmatch.translate(kwargs[globbed_name])
            kwargs[globbed_name] = re.compile(regex)
    _conditions[name] = kwargs


def checkCondition(name, req):
    if name in _conditions:
        condition = _conditions[name]
        # all need to match
        for arg, value in condition.items():
            if arg in _valid_args:
                if not _valid_args[arg](value, req):
                    return False
        return True


def getConditionNames():
    return _conditions.keys()


addCommitCondition("Allow Lockdown Settings Editing",
    path="*/@@lockdown-settings",
    request_method='POST',
    portal_type="Plone Site")
