from zope.i18nmessageid import MessageFactory
from Products.PythonScripts.Utility import allow_module
from Products.CMFCore.DirectoryView import registerDirectory

allow_module('agsci.common')
allow_module('agsci.common.utilities')
allow_module('Products.CMFPlone.utils')
allow_module('plone.app.textfield.value')

AgsciMessageFactory = MessageFactory('agsci.common')
GLOBALS = globals()

registerDirectory('skins/agsci_common', GLOBALS)

# Register indexers
from . import indexer

def initialize(context):
    pass

# Returns an object with the keyword arguments as properties
def object_factory(**kwargs):

    # https://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    class _(object):

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

            # Provide placeholder for empty text
            if not getattr(self, 'text', ''):
                self.text = 'N/A'

    return _(**kwargs)

# Monkey patch hard-coded 2021 year in Products.Archetypes
from DateTime import DateTime

try:
    from Products.Archetypes.browser import datecomponents
except ImportError:
    pass
else:
    datecomponents.PLONE_CEILING = DateTime(2051, 0)

# ZODB Update renames (for Plone 5 migration)
zodbupdate_renames = {
    'App.Product ProductFolder' : 'persistent Persistent',
    'App.interfaces IPersistentExtra' : 'persistent Persistent',
    'App.interfaces IUndoSupport' : 'persistent Persistent',
    'Products.ATContentTypes.interfaces.folder IATBTreeFolder' : 'persistent Persistent',
    'Products.ATContentTypes.interfaces.folder IATFolder' : 'persistent Persistent',
    'Products.ATContentTypes.interfaces.interfaces IATContentType' : 'persistent Persistent',
    'Products.Archetypes.BaseUnit BaseUnit' : 'persistent Persistent',
    'Products.Archetypes.Field FileField' : 'persistent Persistent',
    'Products.Archetypes.Field StringField' : 'persistent Persistent',
    'Products.Archetypes.Storage AttributeStorage' : 'persistent Persistent',
    'Products.Archetypes.Widget BooleanWidget' : 'persistent Persistent',
    'Products.Archetypes.Widget FileWidget' : 'persistent Persistent',
    'Products.Archetypes.Widget MultiSelectionWidget' : 'persistent Persistent',
    'Products.Archetypes.Widget SelectionWidget' : 'persistent Persistent',
    'Products.Archetypes.Widget StringWidget' : 'persistent Persistent',
    'Products.Archetypes.Widget TextAreaWidget' : 'persistent Persistent',
    'Products.Archetypes.interfaces.base IBaseContent' : 'persistent Persistent',
    'Products.Archetypes.interfaces.base IBaseFolder' : 'persistent Persistent',
    'Products.Archetypes.interfaces.base IBaseObject' : 'persistent Persistent',
    'Products.Archetypes.interfaces.metadata IExtensibleMetadata' : 'persistent Persistent',
    'Products.Archetypes.interfaces.referenceable IReferenceable' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields FGBooleanField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields FGFileField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields FGMultiSelectField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields FGSelectionField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields FGStringField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields FGTextField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields NRBooleanField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fields PlainTextField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fieldsBase LinesVocabularyField' : 'persistent Persistent',
    'Products.PloneFormGen.content.fieldsBase StringVocabularyField' : 'persistent Persistent',
    'Products.PloneFormGen.content.form FormFolder' : 'persistent Persistent',
    'Products.PloneFormGen.content.formMailerAdapter FormMailerAdapter' : 'persistent Persistent',
    'Products.PloneFormGen.content.saveDataAdapter FormSaveDataAdapter' : 'persistent Persistent',
    'Products.PloneFormGen.content.thanksPage FormThanksPage' : 'persistent Persistent',
    'Products.PloneFormGen.interfaces.form IPloneFormGenForm' : 'persistent Persistent',
    'Products.PloneFormGen.validators.MaxLengthValidator MaxLengthValidator' : 'persistent Persistent',
    'Products.PloneFormGen.validators.TextValidators LinkSpamValidator' : 'persistent Persistent',
    'Products.ResourceRegistries.interfaces.settings IResourceRegistriesSettings' : 'persistent Persistent',
    'archetypes.multilingual.interfaces IArchetypesTranslatable' : 'persistent Persistent',
    'archetypes.schemaextender.interfaces IExtensible' : 'persistent Persistent',
    'collective.js.jqueryui.controlpanel IJQueryUICSS' : 'persistent Persistent',
    'collective.js.jqueryui.controlpanel IJQueryUIPlugins' : 'persistent Persistent',
    'collective.js.jqueryui.interfaces IJqueryUILayer' : 'persistent Persistent',
    'plone.app.folder.folder IATUnifiedFolder' : 'persistent Persistent',
    'plone.app.imaging.interfaces IBaseObject' : 'persistent Persistent',
    'webdav.EtagSupport EtagBaseInterface' : 'persistent Persistent',
}
