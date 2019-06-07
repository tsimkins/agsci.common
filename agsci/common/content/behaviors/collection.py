from plone.app.contenttypes.behaviors.collection import ICollection as _ICollection
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

# We apparently need two behaviors... One to override, and one to provide fields.

@provider(IFormFieldProvider)
class ICollectionFields(model.Schema):

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=[
            'order_by_id',
            'order_by_title',
            'show_person_areas',
        ],
    )

    order_by_id = schema.List(
        title=_(u"Order by id"),
        description=_(u"The content will show items with the listed ids first, and then sort by the default sort order.  One per line."),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    order_by_title = schema.List(
        title=_(u"Order by Title"),
        description=_(u"The content will show items matching the specified regex patterns first, and then sort by the default sort order.  One per line."),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    show_person_areas = schema.Bool(
        title=_(u"Show 'Areas of Expertise' for people in results."),
        description=_(u""),
        required=False,
    )

@provider(IFormFieldProvider)
class ICollection(_ICollection):

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=[
            'limit',
            'item_count',
        ],
    )

    form.omitted('customViewFields')