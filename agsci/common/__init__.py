from zope.i18nmessageid import MessageFactory
from Products.PythonScripts.Utility import allow_module
from Products.CMFCore.DirectoryView import registerDirectory

allow_module('agsci.common')
allow_module('agsci.common.utilities')

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
from Products.Archetypes.browser import datecomponents
datecomponents.PLONE_CEILING = DateTime(2051, 0)
