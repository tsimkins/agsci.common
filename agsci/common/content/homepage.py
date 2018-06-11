from plone.supermodel import model
from plone.dexterity.content import Item
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider

@provider(IFormFieldProvider)
class IHomePage(model.Schema):
    pass

class HomePage(Item):
    pass