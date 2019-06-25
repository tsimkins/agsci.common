from plone.supermodel import model
from zope import schema
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from zope.interface import Interface, provider, invariant, Invalid, implementer, implements
from plone.app.content.interfaces import INameFromTitle
from zope.component import adapter

from agsci.common import AgsciMessageFactory as _

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
            'employer',
            'club',
            'facility',
            'scholarship',
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
        value_type=schema.Choice(vocabulary="agsci.common.degree.career"),
    )

    employer = schema.TextLine(
        title=_(u"Employers"),
        description=_(u""),
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

    scholarship = schema.List(
        title=_(u"Scholarships"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.common.degree.scholarship"),
    )

class Degree(Container):
    pass

class DegreeContainer(Container):
    pass