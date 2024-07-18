from plone.app.portlets.portlets import base
from zope.interface import implementer

try:
    from plone.base import PloneMessageFactory as _
except ImportError:
    from Products.CMFPlone import PloneMessageFactory as _

from ..tiles.interfaces import ISocialMediaTile as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

@implementer(ITileInterface)
class Assignment(TilePortletAssignment):
    pass

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
