from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.dexterity.content import Container
from zope.interface import provider

@provider(IFormFieldProvider)
class IAgJourneyContainer(model.Schema):
    pass

class AgJourneyContainer(Container):
    pass

@provider(IFormFieldProvider)
class IAgJourney(model.Schema):
    pass

class AgJourney(Container):
    pass