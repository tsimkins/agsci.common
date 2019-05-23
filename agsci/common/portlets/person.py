from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import IAnimalTile
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(IAnimalTile)

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.animal'

class AddForm(base.AddForm):
    schema = IAnimalTile
    
    label = _(u"Add Person Portlet")
    description = _(u"This portlet displays person information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = IAnimalTile

    label = _(u"Edit Person Portlet")
    description = _(u"This portlet displays person information.")