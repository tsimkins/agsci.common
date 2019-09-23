from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider
from plone.autoform import directives as form

from agsci.common import AgsciMessageFactory as _

@provider(IFormFieldProvider)
class ITagsRoot(model.Schema):

    form.write_permission(available_public_tags="cmf.ManagePortal")

    available_public_tags = schema.List(
        title=_(u"Available public tags"),
        description=_(u"Add the tags that will be available for contributors to this blog."),
        value_type=schema.TextLine(required=True),
        required=False,
    )

@provider(IFormFieldProvider)
class IFolderTagsRoot(ITagsRoot):

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=[
            'available_public_tags',
        ],
    )

@provider(IFormFieldProvider)
class ITags(model.Schema):

    model.fieldset(
        'categorization',
        label=_(u'Categorization'),
        fields=(
            'public_tags',
        ),
    )

    public_tags = schema.List(
        title=_(u"Public Tags"),
        description=_(u"Tags for the object that are visible to the public."),
        required=False,
        value_type=schema.Choice(vocabulary="agsci.common.available_public_tags"),
    )