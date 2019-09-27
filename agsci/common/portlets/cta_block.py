from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import IStatlerTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(ITileInterface)

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.statler'

class AddForm(base.AddForm):
    schema = ITileInterface

    label = _(u"Add CTA Block Portlet")
    description = _(u"This portlet displays CTA blocks.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit CTA Block Portlet")
    description = _(u"This portlet displays CTA blocks.")