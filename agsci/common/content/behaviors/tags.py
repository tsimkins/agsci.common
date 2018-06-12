from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

@provider(IFormFieldProvider)
class ITagsRoot(model.Schema):

    available_public_tags = schema.List(
        title=_(u"Available public tags"),
        description=_(u"Add the tags that will be available for contributors to this blog."),
        required=False,
    )

@provider(IFormFieldProvider)
class ITags(model.Schema):

    public_tags = schema.List(
        title=_(u"Public Tags"),
        description=_(u"Tags for the article that are visible to the public."),
        required=False,
    )