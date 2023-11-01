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
    'App.interfaces IPersistentExtra' : 'zope.interface Interface',
    'App.interfaces IUndoSupport' : 'zope.interface Interface',
    'Products.ATContentTypes.interfaces.folder IATBTreeFolder' : 'zope.interface Interface',
    'Products.ATContentTypes.interfaces.folder IATFolder' : 'zope.interface Interface',
    'Products.ATContentTypes.interfaces.interfaces IATContentType' : 'zope.interface Interface',
    'Products.Archetypes.interfaces.base IBaseContent' : 'zope.interface Interface',
    'Products.Archetypes.interfaces.base IBaseFolder' : 'zope.interface Interface',
    'Products.Archetypes.interfaces.base IBaseObject' : 'zope.interface Interface',
    'Products.Archetypes.interfaces.metadata IExtensibleMetadata' : 'zope.interface Interface',
    'Products.Archetypes.interfaces.referenceable IReferenceable' : 'zope.interface Interface',
    'Products.PloneFormGen.interfaces.form IPloneFormGenForm' : 'zope.interface Interface',
    'Products.ResourceRegistries.interfaces.settings IResourceRegistriesSettings' : 'zope.interface Interface',
    'archetypes.multilingual.interfaces IArchetypesTranslatable' : 'zope.interface Interface',
    'archetypes.schemaextender.interfaces IExtensible' : 'zope.interface Interface',
    'collective.js.jqueryui.controlpanel IJQueryUICSS' : 'zope.interface Interface',
    'collective.js.jqueryui.controlpanel IJQueryUIPlugins' : 'zope.interface Interface',
    'collective.js.jqueryui.interfaces IJqueryUILayer' : 'zope.interface Interface',
    'plone.app.folder.folder IATUnifiedFolder' : 'zope.interface Interface',
    'plone.app.imaging.interfaces IBaseObject' : 'zope.interface Interface',
    'OFS.interfaces IFTPAccess': 'zope.interface Interface',
    'Products.CMFCore.interfaces._content ICatalogAware': 'Products.CMFCore.interfaces ICatalogAware',
    'Products.CMFCore.interfaces._content ICatalogableDublinCore': 'Products.CMFCore.interfaces ICatalogableDublinCore',
    'Products.CMFCore.interfaces._content IContentish': 'Products.CMFCore.interfaces IContentish',
    'Products.CMFCore.interfaces._content IDublinCore': 'Products.CMFCore.interfaces IDublinCore',
    'Products.CMFCore.interfaces._content IDynamicType': 'Products.CMFCore.interfaces IDynamicType',
    'Products.CMFCore.interfaces._content IFolderish': 'Products.CMFCore.interfaces IFolderish',
    'Products.CMFCore.interfaces._content IMinimalDublinCore': 'Products.CMFCore.interfaces IMinimalDublinCore',
    'Products.CMFCore.interfaces._content IMutableDublinCore': 'Products.CMFCore.interfaces IMutableDublinCore',
    'Products.CMFCore.interfaces._content IMutableMinimalDublinCore': 'Products.CMFCore.interfaces IMutableMinimalDublinCore',
    'Products.CMFCore.interfaces._content IOpaqueItemManager': 'Products.CMFCore.interfaces IOpaqueItemManager',
    'Products.CMFCore.interfaces._content IWorkflowAware': 'Products.CMFCore.interfaces IWorkflowAware',
    'Products.CMFCore.interfaces._events IActionSucceededEvent': 'Products.CMFCore.interfaces IActionSucceededEvent',
    'Products.CMFPlone.interfaces.controlpanel ILanguageSchema': 'plone.i18n.interfaces ILanguageSchema',
    'webdav.interfaces IWriteLock': 'OFS.interfaces IWriteLock',
    'App.Product ProductFolder' : 'Persistence Persistent',
}
