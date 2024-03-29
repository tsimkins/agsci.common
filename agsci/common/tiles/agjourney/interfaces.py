from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from zope import schema
from zope.interface import Interface

from agsci.common import AgsciMessageFactory as _

class IAgJourneyJumbotronTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
        default=u"Ag Journeys",
    )

    description = schema.TextLine(
        title=_(u"Quote"),
        required=False
    )

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u""),
        required=False,
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


class IAgJourneyBioTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    title_bold = schema.TextLine(
        title=_(u"Title (Bold)"),
        required=False
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u"Image"),
        description=_(u"The image will always be used if it exists."),
        required=False,
    )

    url = schema.TextLine(
        title=_(u"Video URL"),
        description=_(u"The video will be used if no image is provided."),
        required=False,
    )

    video_aspect_ratio = schema.Choice(
        title=_(u"Video Aspect Ratio"),
        vocabulary="agsci.common.tiles.video_aspect_ratio",
        required=True,
        default=u"16:9",
    )

class IQuoteAndImageTile(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    quote_title = schema.Bool(
        title=_(u"Quote Title?"),
        description=_(u""),
        required=False,
        default=False,
    )

    quote_description = schema.Bool(
        title=_(u"Quote Description?"),
        description=_(u""),
        required=False,
        default=False,
    )

    text = RichText(
        title=_(u'Text'),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u"Image 1"),
        description=_(u""),
        required=False,
    )

    image_alt = schema.TextLine(
        title=_(u"Image Alt Text"),
        description=_(u""),
        required=False,
    )

    style = schema.Choice(
        title=_(u"Quote Style"),
        vocabulary='agsci.common.tiles.agjourney.quote_style',
        default=u'plain_image_left',
        required=False,
    )

    padding_top = schema.Bool(
        title=_(u"Padding Top"),
        description=_(u""),
        required=False,
        default=True,
    )

    padding_bottom = schema.Bool(
        title=_(u"Padding Bottom"),
        description=_(u""),
        required=False,
        default=False,
    )
