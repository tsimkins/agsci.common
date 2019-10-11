from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

from ..major import IMajor

@provider(IFormFieldProvider)
class IDegreeContainer(model.Schema):
    pass

@provider(IFormFieldProvider)
class IDegree(model.Schema):

    model.fieldset(
        'categorization',
        label=_(u'Categorization'),
        fields=(
            'interest_area',
            'career',
            'club',
            'facility',
        ),
    )

    options = RichText(
        title=_(u"Options"),
        description=_(u""),
        required=False,
    )

    interest_area = schema.List(
        title=_(u"Interest Areas"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.common.degree.interest_area"),
    )

    career = schema.List(
        title=_(u"Careers"),
        description=_(u""),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    club = schema.List(
        title=_(u"Student Clubs and Organizations"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.common.degree.club"),
    )

    facility = RichText(
        title=_(u"Facilities, Centers, and Institutes"),
        description=_(u""),
        required=False,
    )

    target = RelationChoice(
        title=_(u"Target Major/Degree"),
        source=CatalogSource(object_provides=IMajor.__identifier__),
        required=False,
    )

class Degree(Container):
    pass

class DegreeContainer(Container):
    pass