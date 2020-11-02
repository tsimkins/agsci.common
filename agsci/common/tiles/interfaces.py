from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.app.contenttypes.interfaces import ICollection
from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives as form
from plone.dexterity.interfaces import IDexterityContainer
from plone.namedfile.field import NamedBlobImage
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from agsci.common import AgsciMessageFactory as _

from ..content.behaviors import ISocialContact

class IAgsciTilesLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

# Row Schemas
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

class ISocialMediaTileRowSchema(Interface):

    platform = schema.Choice(
        title=_(u"Social Media Platform"),
        vocabulary='agsci.common.tiles.social_media_platform',
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )

    label = schema.TextLine(
        title=_(u"Label (Optional)"),
        required=False
    )

class IDropdownAccordionRowSchema(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

# Tiles
class IBorderTile(Interface):

    form.order_after(
        border_top='*',
        border_bottom='border_top',
    )

    border_top = schema.Bool(
        title=_(u"Top Border"),
        description=_(u""),
        required=False,
        default=False,
    )

    border_bottom = schema.Bool(
        title=_(u"Bottom Border"),
        description=_(u""),
        required=False,
        default=False,
    )

class IJumbotronTile(Interface):

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

    vertical_align = schema.Choice(
        title=_(u"Vertical Align"),
        vocabulary='agsci.common.tiles.ctb_align',
        default=u'center',
        required=False,
    )

    horizontal_align = schema.Choice(
        title=_(u"Horizontal Align"),
        vocabulary='agsci.common.tiles.clr_align',
        default=u'center',
        required=False,
    )

class ICalloutBlockTile(IBorderTile):

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

class ICTATileBase(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u'Title'),
        default=u'CTA Buttons',
        required=False,
    )

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

    full_width = schema.Bool(
        title=_(u"Full Width?"),
        description=_(u""),
        required=False,
        default=True,
    )

class ICTATile(ICTATileBase):

    form.omitted('title')


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

    image_alt = schema.TextLine(
        title=_(u'Image Alt Text'),
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

class IMissPiggyTile(IBorderTile):

    title = schema.TextLine(
        title=_(u"Title"),
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

    description = schema.TextLine(
        title=_(u'Description'),
        required=False,
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

class IFozzieBearTile(IBorderTile):

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

    count = schema.Choice(
        title=_(u"Count"),
        values=[1,2,3,4],
        required=False,
        default=4,
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

    image_alt = schema.TextLine(
        title=_(u'Image Alt Text'),
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

class IRowlfTile(IBorderTile):

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

    image_alt = schema.TextLine(
        title=_(u'Image Alt Text'),
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

class IScooterTile(IBorderTile):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    target = RelationChoice(
        title=_(u"Target Collection"),
        source=CatalogSource(object_provides=ICollection.__identifier__),
        required=False,
    )

    target_container = RelationChoice(
        title=_(u"Target Container"),
        source=CatalogSource(object_provides=IDexterityContainer.__identifier__),
        required=False,
    )

    exclude_navigation = schema.Bool(
        title=_(u"Hide items excluded from navigation"),
        required=False,
        default=False,
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

class ISkeeterTile(IBorderTile):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    target = RelationChoice(
        title=_(u"Target Collection"),
        source=CatalogSource(object_provides=ICollection.__identifier__),
        required=False,
    )

    target_container = RelationChoice(
        title=_(u"Target Container"),
        source=CatalogSource(object_provides=IDexterityContainer.__identifier__),
        required=False,
    )

    exclude_navigation = schema.Bool(
        title=_(u"Hide items excluded from navigation"),
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

    filter_tags = schema.List(
        title=_(u"Filter By Tag(s)"),
        value_type=schema.Choice(vocabulary="agsci.common.tiles.tags"),
        required=False,
    )

    filter_public_tags = schema.List(
        title=_(u"Filter By Public Tag(s)"),
        value_type=schema.Choice(vocabulary="agsci.common.tiles.public_tags"),
        required=False,
    )

    light_version = schema.Bool(
        title=_(u"Light Version? (for News Condensed and Events)"),
        description=_(u""),
        required=False,
        default=False,
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

    style = schema.Choice(
        title=_(u"Style"),
        vocabulary='agsci.common.tiles.hv_orientation',
        default=u'horizontal',
        required=False,
    )

    show_image = schema.Bool(
        title=_(u"Show Person Image?"),
        description=_(u""),
        required=False,
        default=True,
    )

    count = schema.Choice(
        title=_(u"Count"),
        values=[1,2,3,4],
        default=1,
        required=True,
    )

class IPepeTheKingPrawnTile(IGonzoTile):
    pass

class IRizzoTheRatTile(ISocialContact, Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    directions = schema.TextLine(
        title=_(u"Directions"),
        required=False,
    )

    hours = schema.TextLine(
        title=_(u"Hours"),
        required=False,
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


class IYouTubeTile(IBorderTile):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
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

    full_width = schema.Bool(
        title=_(u"Full Width?"),
        description=_(u""),
        required=False,
        default=False,
    )

class IDropdownAccordionTile(IBorderTile):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    label = schema.TextLine(
        title=_(u"Label"),
        required=False
    )

    value = schema.List(
        title=u"Items",
        value_type=DictRow(title=u"Items", schema=IDropdownAccordionRowSchema),
        required=False
    )

    show_images = schema.Bool(
        title=_(u"Show Images?"),
        description=_(u"Show images in the accordion. The image fields below correspond with the rows in the table above."),
        required=False,
        default=True,
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

    image_4 = NamedBlobImage(
        title=_(u"Image 5"),
        description=_(u""),
        required=False,
    )

    image_alt_5 = schema.TextLine(
        title=_(u"Image 5 Alt Text"),
        description=_(u""),
        required=False,
    )

class IExploreMoreTile(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.List(
        title=u"Items",
        value_type=DictRow(title=u"Items", schema=IDropdownAccordionRowSchema),
        required=False
    )

class ISocialMediaTile(Interface):

    form.widget(value=DataGridFieldFactory)

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.List(
        title=u"Platforms",
        value_type=DictRow(title=u"Items", schema=ISocialMediaTileRowSchema),
        required=False
    )

class IPortletsTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )


class IRichTextTile(IBorderTile):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

    full_width = schema.Bool(
        title=_(u"Full Width?"),
        description=_(u""),
        required=False,
        default=False,
    )

class IPullQuoteTile(Interface):

    quote = schema.TextLine(
        title=_(u"Quote"),
        required=False
    )

    speaker = schema.TextLine(
        title=_(u"Speaker"),
        required=False
    )

    speaker_title = schema.TextLine(
        title=_(u"Speaker Title"),
        required=False
    )

class ISearchBoxTile(IBorderTile):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    target_container = RelationChoice(
        title=_(u"Target Container"),
        source=CatalogSource(object_provides=IDexterityContainer.__identifier__),
        required=False,
    )

    placeholder_text = schema.TextLine(
        title=_(u"Placeholder Text"),
        required=False
    )