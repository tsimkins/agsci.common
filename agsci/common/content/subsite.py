from plone.supermodel import model
from plone.dexterity.content import Container
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider

@provider(IFormFieldProvider)
class ISubsite(model.Schema):
    pass

class Subsite(Container):
    pass