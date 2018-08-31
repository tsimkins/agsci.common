from agsci.common import AgsciMessageFactory as _

from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform import directives as form

class ITestTileRowSchema(Interface):

    value = schema.TextLine(
        title=_(u"Value"),
        required=False
    )

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )


class ICollectionTileRenderer(Interface):
    """
    """

class IAgsciTilesLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ITestTile(model.Schema):


    title = schema.TextLine(
        title=_(u'Tile title'),
        required=False,
    )

    description = schema.TextLine(
        title=_(u'Description'),
        required=False,
    )
    
    values = schema.List(
        title=u"Values",
        value_type=schema.TextLine(required=True),
        required=False
    )

