from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from zope.interface import implements

from ..tiles.interfaces import ISocialMediaTile
from . import TilePortletAssignment, TilePortletRenderer

class Assignment(TilePortletAssignment):
    implements(ISocialMediaTile)

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.social_media'

class AddForm(base.AddForm):
    schema = ISocialMediaTile
    
    label = _(u"Add Social Media Portlet")
    description = _(u"This portlet displays social media information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ISocialMediaTile

    label = _(u"Edit Social Media Portlet")
    description = _(u"This portlet displays social media information.")