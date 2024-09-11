from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

@provider(IFormFieldProvider)
class IAccordionFolder(model.Schema):
    pass

class AccordionFolder(Container):
    pass

@provider(IFormFieldProvider)
class IAccordionPage(model.Schema):

    exclude_from_robots = schema.Bool(
        title=_(u"Exclude from search engines"),
        description=_(u"Add to robots.txt file and add meta tag to header."),
        required=False,
        default=True,
    )

class AccordionPage(Container):
    pass
