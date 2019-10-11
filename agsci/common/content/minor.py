from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import provider

@provider(IFormFieldProvider)
class IMinor(model.Schema):
    pass

class Minor(Container):
    pass