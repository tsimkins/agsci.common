from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.app.vocabularies.catalog import CatalogSource
from plone.namedfile.field import NamedBlobImage
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface

from agsci.common import AgsciMessageFactory as _

from .. import IBorderTile
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