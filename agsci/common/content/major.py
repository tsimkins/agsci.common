from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import provider

@provider(IFormFieldProvider)
class IMajor(model.Schema):
    pass

class Major(Container):
    pass