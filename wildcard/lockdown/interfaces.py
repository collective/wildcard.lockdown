from zope import schema
from wildcard.lockdown import _
from zope.interface import Interface


class ILayer(Interface):
    pass


class ISettings(Interface):
    enabled = schema.Bool(
        title=_(u"Enabled"),
        description=_(u"If enabled, it'll by default make the entire site "
                      u"read-only unless it's in debug mode or one of the "
                      u"activated conditions are met. Basically, this could "
                      u"mean that you will prevent yourself from disabling "
                      u"this feature unless you uninstall the package."),
        default=False
        )

    activated = schema.Set(
        title=_(u"Activated Commit Conditions"),
        description=_(u"Select the conditions under which something can be "
                      u"committed to the database. Only one rules needs to "
                      u"be valid to allow commits to occur."),
        value_type=schema.Choice(vocabulary=u"wildcard.lockdown.conditions"),
        default=set([]),
        missing_value=set([]),
        required=False
        )
