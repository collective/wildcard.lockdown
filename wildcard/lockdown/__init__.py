from zope.i18nmessageid import MessageFactory
import fnmatch
import re

_ = MessageFactory('collective.routes')


def _checkPath(regex, req):
    url = req.get('ACTUAL_URL', '')
    if regex.matches(url):
        return True
    return False


def _checkRequestMethod(method, req):
    req_meth = req.get('REQUEST_METHOD', '')
    return method == req_meth


def _checkPortalType(pt, req):
    portal_type = getattr(req.published, 'portal_type', None)
    return portal_type == pt


def _checkDomain(domain, req):
    req_domain = req.get('Host')
    return req_domain == domain


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
