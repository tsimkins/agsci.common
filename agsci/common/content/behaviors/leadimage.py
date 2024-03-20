from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior as _ILeadImage
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.file import NamedBlobImage as _NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import provider, implementer

from agsci.common import AgsciMessageFactory as _
from agsci.common.constants import IMAGE_FORMATS
from agsci.common.interfaces import ILeadImageMarker
from agsci.common.permissions import DIRECTORY_EDITOR
from ..person.person import IPerson

@provider(IFormFieldProvider)
class ILeadImage(_ILeadImage):
    pass

@provider(IFormFieldProvider)
class ILeadImageNoCaption(ILeadImage):
    form.omitted('image_caption')
    form.write_permission(image=DIRECTORY_EDITOR)

@provider(IFormFieldProvider)
class ILeadImageExtra(ILeadImage):

    form.write_permission(image_show_jumbotron="cmf.ManagePortal")

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=(
            'image_full_width',
            'image_quarter_width',
            'image_show',
            'image_show_jumbotron',
        ),
    )

    image_full_width = schema.Bool(
        title=_(u"Full width lead image"),
        description=_(u"This will show a large lead image on the object display."),
        default=True,
        required=False,
    )

    image_quarter_width = schema.Bool(
        title=_(u"Quarter width lead image"),
        description=_(u"This will show a small lead image on the object display."),
        default=False,
        required=False,
    )

    image_show = schema.Bool(
        title=_(u"Show Lead Image on this item"),
        description=_(u"This will show the lead image on the object display."),
        default=True,
        required=False,
    )

    image_show_jumbotron = schema.Bool(
        title=_(u"Show Lead Image as Jumbtron"),
        description=_(u"Shows the image above the content as a jumbotron."),
        default=False,
        required=False,
    )

@adapter(IDexterityContent)
@implementer(ILeadImageMarker)
class LeadImage(object):

    exclude_interfaces = [
        IPerson,
    ]

    def __init__(self, context):
        self.context = context

    @property
    def image_caption(self):
        return getattr(self.context, "image_caption", None)

    @property
    def image_full_width(self):
        if not self.image_quarter_width:
            return getattr(self.context, "image_full_width", False)

    @property
    def image_quarter_width(self):
        return getattr(self.context, "image_quarter_width", False)

    @property
    def image_show(self):

        if not self.image_show_jumbotron:

            if not any([x.providedBy(self.context) for x in self.exclude_interfaces]):
                return getattr(self.context, "image_show", True)

        return False

    @property
    def image_show_jumbotron(self):

        if not any([x.providedBy(self.context) for x in self.exclude_interfaces]):
            return getattr(self.context, "image_show_jumbotron", True)

        return False

    @property
    def has_image(self):
        image = getattr(self.context, 'image', None)

        if image and hasattr(image, 'size') and image.size > 0:
            return True

        return False

    @property
    def images(self):
        return self.context.restrictedTraverse('@@images')

    def tag(self, css_class='w-100', scale='large'):

        if self.has_image:

            alt = getattr(self.context, 'image_caption', '')

            return self.images.tag('image', scale=scale, alt=alt, css_class=css_class)

        return None

    @property
    def img_src(self):

        return self.get_img_src()

    def get_img_src(self, scale=None):

        if self.has_image:

            return self.images.scale('image', scale=scale).url

        return None

    def get_image(self):
        if self.has_image:
            return getattr(self.context, 'image')

        return None

    def set_image(self, data):
        field = _NamedBlobImage(filename=u'image', data=data)
        self.context.image = field

    @property
    def image_format_data(self):

        default = [None, None]

        if self.has_image:
            return IMAGE_FORMATS.get(self.get_image().contentType, default)

        return default

    @property
    def image_extension(self):
        return self.image_format_data[1]

    @property
    def image_format(self):
        return self.image_format_data[0]
