from Products.CMFPlone import PloneMessageFactory as _
from plone.autoform import directives as form
from plone.app.contenttypes.interfaces import ICollection
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import CatalogSource
from zope.interface import implementer
from zope import schema

from ..tiles.interfaces import ISkeeterTile
from . import TilePortletAssignment, TilePortletRenderer

class ITileInterface(ISkeeterTile):

    form.order_after(target='title')
    form.omitted('featured_id')

    target = schema.Choice(
        title=_(u"Target Collection"),
        source=CatalogSource(object_provides=ICollection.__identifier__),
        required=False,
    )

@implementer(ITileInterface)
class Assignment(TilePortletAssignment):
    pass

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.skeeter'

class AddForm(base.AddForm):
    schema = ITileInterface

    label = _(u"Add News/Event Listing Portlet")
    description = _(u"This portlet displays news/event listings.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit News/Event Listing Portlet")
    description = _(u"This portlet displays news/event listings.")
