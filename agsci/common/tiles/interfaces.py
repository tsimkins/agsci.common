from agsci.common import AgsciMessageFactory as _
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from plone.app.textfield import RichText
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform import directives as form
from plone.namedfile.field import NamedBlobImage

class IAgsciTilesLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class ICTATileRowSchema(Interface):

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
        description=_(u"Frequency that reports will be emailed."),
        values=[u'orange', u'purple', u'green'],
        default=u'orange',
        required=False,
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

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    value = schema.List(
        title=u"Buttons",
        value_type=DictRow(title=u"Button", schema=ICTATileRowSchema),
        #value_type=schema.TextLine(required=True),
        required=False
    )
