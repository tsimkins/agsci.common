from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import IRizzoTheRatTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(ITileInterface)

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.rizzo_the_rat'

class AddForm(base.AddForm):
    schema = ITileInterface
    
    label = _(u"Add Office Address Information Portlet")
    description = _(u"This portlet displays office address information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit Office Address Information Portlet")
    description = _(u"This portlet displays office address information.")