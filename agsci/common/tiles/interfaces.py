from agsci.common import AgsciMessageFactory as _
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.app.textfield import RichText
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage

button_colors = [u'orange', u'purple', u'green']

class IAgsciTilesLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IButtonTileRowSchema(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )
    
    color = schema.Choice(
        title=_(u"Button Color"),
        values=button_colors,
        default=u'orange',
        required=False,
    )

class IButtonBlockTileRowSchema(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    label = schema.TextLine(
        title=_(u"Label"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )
    
    color = schema.Choice(
        title=_(u"Button Color"),
        values=button_colors,
        default=u'orange',
        required=False,
    )

class IItemBlockTileRowSchema(Interface):

    value = schema.TextLine(
        title=_(u"Value"),
        required=False
    )

    label = schema.TextLine(
        title=_(u"Label"),
        required=False
    )

class IJumbotronTile(model.Schema):

    title = schema.TextLine(
        title=_(u'Tile title'),
        required=False,
    )

    description = schema.TextLine(
        title=_(u'Description'),
        required=False,
    )
    
    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
        required=False,
    )

    show_title = schema.Bool(
        title=_(u"Show Title?"),
        description=_(u""),
        required=False,
        default=True,
    )
    
    show_description = schema.Bool(
        title=_(u"Show Description?"),
        description=_(u""),
        required=False,
        default=False,
    )

    show_breadcrumbs = schema.Bool(
        title=_(u"Show Breadcrumbs?"),
        description=_(u""),
        required=False,
        default=True,
    )

class ICalloutBlockTile(model.Schema):

    title = schema.TextLine(
        title=_(u'Tile title'),
        required=False,
    )
    
    description = schema.TextLine(
        title=_(u'Description'),
        required=False,
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

class ICTATile(Interface):

    form.widget(value=DataGridFieldFactory)

    value = schema.List(
        title=u"Buttons",
        value_type=DictRow(title=u"Button", schema=IButtonTileRowSchema),
        required=False
    )

class IKermitTile(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

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

class IMissPiggyTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
        required=False,
    )

    description = schema.TextLine(
        title=_(u'Description'),
        required=False,
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

class IFozzieBearTile(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.List(
        title=u"Items",
        value_type=DictRow(title=u"Items", schema=IItemBlockTileRowSchema),
        required=False
    )

class IGonzoTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
        required=False,
    )

    image_align = schema.Choice(
        title=_(u"Image Align"),
        values=['left', 'right'],
        default=u'right',
        required=False,
    )

    label = schema.TextLine(
        title=_(u"Label"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )
    