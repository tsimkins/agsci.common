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
from ..person.person import IPerson

@provider(IFormFieldProvider)
class ILeadImage(_ILeadImage):
    pass

@provider(IFormFieldProvider)
class ILeadImageNoCaption(ILeadImage):
    form.omitted('image_caption')

@provider(IFormFieldProvider)
class ILeadImageExtra(ILeadImage):

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=(
            'image_full_width',
            'image_show',
        ),
    )

    image_full_width = schema.Bool(
        title=_(u"Full width lead image"),
        description=_(u"This will show a large lead image on the object display."),
        default=True,
        required=False,
    )

    image_show = schema.Bool(
        title=_(u"Show Lead Image on this item"),
        description=_(u"This will show the lead image on the object display."),
        default=True,
        required=False,
    )

@implementer(ILeadImage)
@adapter(IDexterityContent)
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
        return getattr(self.context, "image_full_width", False)

    @property
    def image_show(self):

        if not any([x.providedBy(self.context) for x in self.exclude_interfaces]):
            return getattr(self.context, "image_show", True)

        return False

    @property
    def has_image(self):
        image = getattr(self.context, 'image', None)

        if image and hasattr(image, 'size') and image.size > 0:
            return True

        return False

    def tag(self, css_class='w-100', scale='large'):

        alt = getattr(self.context, 'image_caption', '')

        images = self.context.restrictedTraverse('@@images')

        if self.has_image:
            return images.tag('image', scale=scale, alt=alt, css_class=css_class)

        return None

    def get_image(self):
        if self.has_image:
            return getattr(self.context, 'image')

        return None

    def set_image(self, data):
        field = _NamedBlobImage(filename=u'image')
        field.data = data
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