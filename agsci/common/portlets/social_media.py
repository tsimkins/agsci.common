from zope import schema
from zope.component import getMultiAdapter
from zope.interface import implements
from plone.memoize.compress import xhtml_compress

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_chain
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.interfaces import IPloneSiteRoot

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

from .. import object_factory
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
