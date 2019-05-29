from plone.supermodel import model
from plone.dexterity.content import Container
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider

@provider(IFormFieldProvider)
class IMajor(model.Schema):
    pass

class Major(Container):
    pass