from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import ISkeeterTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(ITileInterface)

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