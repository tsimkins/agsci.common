from Acquisition import aq_chain
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

try:
    from plone.base.interfaces.siteroot import ISiteRoot
except ImportError:
    from Products.CMFPlone.interfaces.siteroot import ISiteRoot

from agsci.common import AgsciMessageFactory as _

@provider(IContextAwareDefaultFactory)
def defaultCounty(context):

    for o in aq_chain(context):
        if ISiteRoot.providedBy(o):
            break

        _ = getattr(o.aq_base, 'county', [])

        if _ and isinstance(_, (list, tuple)):
            return list(_)

    return []

@provider(IFormFieldProvider)
class ICounty(model.Schema):

    model.fieldset(
        'categorization',
        label=_(u'Categorization'),
        fields=('county',),
    )

    county = schema.List(
        title=_(u"County"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.common.programs.County"),
        required=False,
        defaultFactory=defaultCounty,
    )

@provider(IFormFieldProvider)
class ICountyContainer(ICounty):

    county = schema.List(
        title=_(u"County"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.common.programs.County"),
        required=False,
    )
