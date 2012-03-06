from zope import schema
from plone.app.theming.interfaces import _
from zope.interface import Interface


class ILayer(Interface):
    pass


class ISettings(Interface):
    enabled = schema.Bool(
        title=_(u"Enabled"),
        description=_(u"If enabled, it'll by default make the entire site "
                      u"read-only unless it's in debug mode or one of the "
                      u"activated conditions are met. Basically, this could "
                      u"mean that you will provent yourself from disabling "
                      u"this feature.")
        )

    activated = schema.Set(
        title=_(u"Activated Commit Conditions"),
        description=_(u"Select the conditions under which something can be "
                      u"committed to the database"),
        value_type=schema.Choice(vocabulary=u"wildcard.lockdown.conditions"),
        default=set([]),
        missing_value=set([]),
        required=False,
        )
