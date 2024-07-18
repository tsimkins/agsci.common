from plone.app.portlets.portlets import base
from zope.interface import implementer

try:
    from plone.base import PloneMessageFactory as _
except ImportError:
    from Products.CMFPlone import PloneMessageFactory as _

from ..tiles.interfaces import ICTATileBase as ITileInterface
from . import TilePortletAssignment, TilePortletRenderer

@implementer(ITileInterface)
class Assignment(TilePortletAssignment):
    pass

class Renderer(TilePortletRenderer):
    tile_name = 'agsci.common.tiles.cta'

class AddForm(base.AddForm):
    schema = ITileInterface

    label = _(u"Add CTA Button Portlet")
    description = _(u"This portlet displays CTA buttons.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITileInterface

    label = _(u"Edit CTA Button Portlet")
    description = _(u"This portlet displays CTA buttons.")
