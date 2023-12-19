from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from plone.app.contenttypes.interfaces import ICollection
from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface

from agsci.common import AgsciMessageFactory as _

from ..interfaces import IDropdownAccordionRowSchema, IButtonBlockTileRowSchema

class IJumbotronTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
        required=False,
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

class IRolloverPanelsTile(Interface):

    form.widget(value=DataGridFieldFactory)

    value = schema.List(
        title=u"Items",
        value_type=DictRow(title=u"Items", schema=IDropdownAccordionRowSchema),
        required=False
    )

    image_0 = NamedBlobImage(
        title=_(u"Image 1"),
        description=_(u""),
        required=False,
    )

    image_alt_0 = schema.TextLine(
        title=_(u"Image 1 Alt Text"),
        description=_(u""),
        required=False,
    )

    image_1 = NamedBlobImage(
        title=_(u"Image 2"),
        description=_(u""),
        required=False,
    )

    image_alt_1 = schema.TextLine(
        title=_(u"Image 2 Alt Text"),
        description=_(u""),
        required=False,
    )

    image_2 = NamedBlobImage(
        title=_(u"Image 3"),
        description=_(u""),
        required=False,
    )

    image_alt_2 = schema.TextLine(
        title=_(u"Image 3 Alt Text"),
        description=_(u""),
        required=False,
    )

    image_3 = NamedBlobImage(
        title=_(u"Image 4"),
        description=_(u""),
        required=False,
    )

    image_alt_3 = schema.TextLine(
        title=_(u"Image 4 Alt Text"),
        description=_(u""),
        required=False,
    )


class ICallToActionImageAndBlocksTile(Interface):

    form.widget(value=DataGridFieldFactory)

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
        required=False,
    )

    value = schema.List(
        title=u"Buttons",
        value_type=DictRow(title=u"Button", schema=IButtonBlockTileRowSchema),
        required=False
    )


class INewsAndEventsTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    target_news = RelationChoice(
        title=_(u"Target News Collection"),
        source=CatalogSource(object_provides=ICollection.__identifier__),
        required=False,
    )

    target_events = RelationChoice(
        title=_(u"Target Events Collection"),
        source=CatalogSource(object_provides=ICollection.__identifier__),
        required=False,
    )


class IExtensionListingTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    product_types = schema.List(
        title=_(u"Show Product Types"),
        value_type=schema.Choice(vocabulary="agsci.common.tiles.extension_homepage.product_types"),
        required=False,
    )

    count = schema.Choice(
        title=_(u"Count"),
        values=[1,2,3,4],
        required=False,
    )

    style = schema.Choice(
        title=_(u"Card Style"),
        vocabulary='agsci.common.tiles.card_style',
        default=u'image',
        required=False,
    )

    show_item_title = schema.Bool(
        title=_(u"Show Item Title?"),
        description=_(u"(For Image card style)"),
        required=False,
        default=True,
    )

class IExtensionFilteredListingTile(IExtensionListingTile):

    department_id = schema.Choice(
        title=_(u"Department"),
        vocabulary='agsci.common.tiles.extension_homepage.departments',
        required=False,
    )

    category = schema.Choice(
        title=_(u"Category"),
        vocabulary='agsci.common.tiles.extension_homepage.l1_categories',
        required=False,
    )

class IExtensionSKUFilteredListingTile(IExtensionListingTile):

    department_id = schema.Choice(
        title=_(u"Department"),
        vocabulary='agsci.common.tiles.extension_homepage.departments',
        required=False,
    )

    skus = schema.List(
        title=u"SKUs",
        value_type=schema.TextLine(required=True),
        required=False
    )

    sku_order = schema.List(
        title=u"SKU Order",
        value_type=schema.TextLine(required=True),
        required=False
    )
