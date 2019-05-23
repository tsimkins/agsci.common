from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import ISocialMediaTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(ITileInterface)

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.social_media'

class AddForm(base.AddForm):
    schema = ITileInterface
    
    label = _(u"Add Social Media Portlet")
    description = _(u"This portlet displays social media information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit Social Media Portlet")
    description = _(u"This portlet displays social media information.")