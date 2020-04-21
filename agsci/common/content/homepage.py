from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import provider

@provider(IFormFieldProvider)
class IHomepage(model.Schema):
    pass

class Homepage(Item):
    pass

@provider(IFormFieldProvider)
class ICollegeHomepage(IHomepage):
    pass

class CollegeHomepage(Homepage):
    pass

@provider(IFormFieldProvider)
class IExtensionHomepage(IHomepage):
    pass

class ExtensionHomepage(Homepage):
    pass