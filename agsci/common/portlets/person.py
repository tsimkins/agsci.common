from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implementer

from ..tiles.interfaces import IAnimalTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

@implementer(ITileInterface)
class Assignment(TilePortletAssignment):
    pass

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.animal'

class AddForm(base.AddForm):
    schema = ITileInterface

    label = _(u"Add Person Portlet")
    description = _(u"This portlet displays person information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit Person Portlet")
    description = _(u"This portlet displays person information.")
