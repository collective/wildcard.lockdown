from plone.app.registry.browser import controlpanel
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from wildcard.lockdown import _
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from wildcard.lockdown import getConditionNames
from wildcard.lockdown.interfaces import ISettings


class ConditionsVocabulary(object):
    """Creates a vocabulary with all the routes available on the
    site.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = []
        for name in getConditionNames():
            items.append(SimpleVocabulary.createTerm(name,
                                                     name,
                                                     name))
        return SimpleVocabulary(items)
ConditionsVocabularyFactory = ConditionsVocabulary()


class LockdownSettingsEditForm(controlpanel.RegistryEditForm):
    schema = ISettings
    label = _(u'Lockdown Settings')
    description = _(u'Here you can modify the settings for '
                    u'locking down writes to database.')

    def updateFields(self):
        super(LockdownSettingsEditForm, self).updateFields()
        self.fields['activated'].widgetFactory = CheckBoxFieldWidget


class LockdownConfiglet(controlpanel.ControlPanelFormWrapper):
    form = LockdownSettingsEditForm
