"""View to manage lockdown settings."""

from ..interfaces import ISettings
from Products.Five.browser import BrowserView
from plone import api
from wildcard.lockdown import logger
import json

MISSING = object()


class ManageLockdownView(BrowserView):
    """View to get and set lockdown settings.

    See: README
    """

    def __init__(self, context, request):
        """Constructor."""
        BrowserView.__init__(self, context, request)
        self.response = request.response

    def __call__(self):
        """Configure lockdown settings."""
        options = self.request.form
        raise_exceptions = options.pop('_raise_exceptions', False)
        method = self.request.get('REQUEST_METHOD')

        if options and (method != 'POST'):
            return self._error_response(
                u'To set options use the POST HTTP method.',
                status=405
            )

        if method == 'POST':
            return self._set_options(options, raise_exceptions=raise_exceptions)
        elif method == 'GET':
            return self._get_options()

        return self._error_response(u'Invalid HTTP method.', status=405)

    def _set_options(self, options, raise_exceptions=False):
        for (k, v) in options.iteritems():
            logger.info(
                'Setting "{name}" to {value} {type}'.format(
                    name=k,
                    value=repr(v),
                    type=type(v)
                ))
            try:
                self._set_option(k, self._convert_input_value(v))
            except Exception as e:
                if raise_exceptions:
                    raise
                return self._error_response(unicode(e))

        return self._json_response(u'OK', status=200)

    def _get_options(self):
        return self._json_response({
            name: self._convert_output_value(self._get_option(name))
            for name in ISettings
        })

    def _set_option(self, name, value):
        api.portal.set_registry_record(name=name, value=value, interface=ISettings)

    def _get_option(self, name):
        return api.portal.get_registry_record(name=name, interface=ISettings)

    def _convert_output_value(self, v):
        if isinstance(v, set):
            return list(v)
        return v

    def _convert_input_value(self, v):
        if isinstance(v, list):
            return set(v)
        return v

    def _response(self, data, content_type, status=200):
        self.response.setHeader('Content-Type', content_type)
        self.response.setStatus(status)
        return data

    def _json_response(self, data, status=200):
        return self._response(
            data=json.dumps(data),
            content_type='application/json; charset=utf-8',
            status=status
        )

    def _error_response(self, message, status=500):
        return self._json_response({'error': message}, status=status)
