from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import IScooterTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(ITileInterface)

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.scooter'

class AddForm(base.AddForm):
    schema = ITileInterface

    label = _(u"Add Card Listing Portlet")
    description = _(u"This portlet displays card listings.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit Card Listing Portlet")
    description = _(u"This portlet displays card listings.")