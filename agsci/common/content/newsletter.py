from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.supermodel import model
from plone.dexterity.content import Item
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import provider, Interface
from plone.app.vocabularies.catalog import CatalogSource
from z3c.relationfield.schema import RelationChoice
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.contenttypes.interfaces import ICollection

from agsci.common import AgsciMessageFactory as _

class INewsletterItemsRowSchema(Interface):

    target = RelationChoice(
        title=_(u"News Item"),
        source=CatalogSource(object_provides=INewsItem.__identifier__),
        required=False,
    )

    spotlight = schema.Bool(
        title=_(u"Spotlight"),
        required=False,
        default=False,
    )

@provider(IFormFieldProvider)
class INewsletter(model.Schema):

    form.widget(value=DataGridFieldFactory)

    target = RelationChoice(
        title=_(u"Target Collection"),
        source=CatalogSource(object_provides=ICollection.__identifier__),
        required=False,
    )

    show_summary = schema.Choice(
        title=_(u"Enabled"),
        required=False,
        values = ['yes', 'no', 'auto'],
        default='auto',
    )

    limit = schema.Choice(
        title=_(u"Months to Limit"),
        required=False,
        values = [1, 3, 6, 9, 12],
        default=1,
    )

    value = schema.List(
        title=u"News Items",
        value_type=DictRow(title=u"News Item", schema=INewsletterItemsRowSchema),
        required=False
    )

    listserv_email = schema.TextLine(
        title=_(u"Listserv Email"),
        description=_(u"[Listserv Name]@lists.psu.edu"),
        required=False,
    )


class Newsletter(Item):
    pass