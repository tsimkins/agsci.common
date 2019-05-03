from agsci.common import AgsciMessageFactory as _
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.app.textfield import RichText
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage

from ..content.behaviors import ISocialContact

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
        vocabulary='agsci.common.tiles.button_colors',
        default=u'orange',
        required=False,
    )

class IPersonTileRowSchema(Interface):

    username = schema.Choice(
        title=_(u"Name"),
        vocabulary='agsci.common.tiles.people',
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
        vocabulary='agsci.common.tiles.button_colors',
        default=u'orange',
        required=False,
    )

class IItemBlockTileRowSchema(Interface):

    pre = schema.TextLine(
        title=_(u"Pre-value Text"),
        required=False
    )

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
        title=_(u'Title'),
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
        title=_(u'Title'),
        required=False,
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

    text_align = schema.Choice(
        title=_(u"Text Align"),
        vocabulary='agsci.common.tiles.lc_align',
        default=u'left',
        required=False,
    )

class ICTATile(Interface):

    form.widget(value=DataGridFieldFactory)

    background = schema.Choice(
        title=_(u"Background"),
        vocabulary='agsci.common.tiles.cta_background',
        default=u'light',
        required=True,
    )

    value = schema.List(
        title=u"Buttons",
        description=u"Default order: Orange, Green, Purple",
        value_type=DictRow(title=u"Button", schema=IButtonTileRowSchema),
        required=False
    )

class ILargeCTATile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    text = RichText(
        title=_(u'Text'),
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

    full_width = schema.Bool(
        title=_(u"Full Width?"),
        description=_(u""),
        required=False,
        default=True,
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

    style = schema.Choice(
        title=_(u"Style"),
        vocabulary='agsci.common.tiles.cta_background',
        default=u'light',
        required=True,
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
        vocabulary='agsci.common.tiles.lr_align',
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

    full_width = schema.Bool(
        title=_(u"Full Width?"),
        description=_(u""),
        required=False,
        default=True,
    )

class IRowlfTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    caption = schema.TextLine(
        title=_(u"Caption"),
        required=False
    )

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
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

class IScooterTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.TextLine(
        title=_(u"Items"),
        required=False
    )

    count = schema.Choice(
        title=_(u"Count"),
        values=[2,3,4],
        required=False,
    )

    style = schema.Choice(
        title=_(u"Card Style"),
        vocabulary='agsci.common.tiles.card_style',
        default=u'image',
        required=False,
    )

class ISkeeterTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.TextLine(
        title=_(u"Items"),
        required=False
    )

    show_description = schema.Bool(
        title=_(u"Show Item Description?"),
        description=_(u""),
        required=False,
        default=False,
    )

    featured_id = schema.TextLine(
        title=_(u"Featured Item Id"),
        description=_(u"Short name of featured item"),
        required=False
    )

    style = schema.Choice(
        title=_(u"Style"),
        vocabulary='agsci.common.tiles.feature_card_style',
        default=u'news',
        required=False,
    )

class IAnimalTile(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.List(
        title=u"People",
        description=u"",
        value_type=DictRow(title=u"Person", schema=IPersonTileRowSchema),
        required=False
    )

    count = schema.Choice(
        title=_(u"Count"),
        values=[1,2,3,4],
        default=1,
        required=True,
    )

    style = schema.Choice(
        title=_(u"Orientation"),
        vocabulary='agsci.common.tiles.hv_orientation',
        default='vertical',
        required=True,
    )

class IPepeTheKingPrawnTile(IGonzoTile):
    pass

class IRizzoTheRatTile(ISocialContact, Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    form.order_before(title='*')


class IStatlerTile(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    show_title = schema.Bool(
        title=_(u"Show Title?"),
        description=_(u""),
        required=False,
        default=True,
    )

    value = schema.List(
        title=u"Buttons",
        value_type=DictRow(title=u"Cards", schema=IButtonBlockTileRowSchema),
        required=False
    )

    count = schema.Choice(
        title=_(u"Count"),
        values=[1,2,3,4],
        default=1,
        required=True,
    )


class IYouTubeTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"Video URL"),
        required=True,
    )

    video_aspect_ratio = schema.Choice(
        title=_(u"Video Aspect Ratio"),
        vocabulary="agsci.common.tiles.video_aspect_ratio",
        required=True,
        default=u"16:9",
    )