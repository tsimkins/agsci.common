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

from agsci.common.interfaces import ITagsAdapter
from ..content.behaviors.tags import ITagsRoot

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

class ITag(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    show_header = schema.Bool(
        title=_(u"Show portlet header"),
        description=_(u""),
        required=True,
        default=False)

class Assignment(base.Assignment):

    implements(ITag)

    header = ""
    show_header = False

    def __init__(self, header=u"", show_header=False, *args, **kwargs):
        base.Assignment.__init__(self, *args, **kwargs)
        self.header = header
        self.show_header = show_header
                
    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return "Tags"


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/tags.pt')

    target_view = "tags"

    @property
    def adapted(self):
        return ITagsAdapter(self.context)

    @property
    def tags(self):
        return self.adapted.selected_tags

    @property
    def parent_object(self):
        return self.adapted.parent_object

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.tags


class AddForm(base.AddForm):
    schema = ITag
    
    label = _(u"Add Tag Portlet")
    description = _(u"This portlet displays tag information.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    schema = ITag

    label = _(u"Edit Tag Portlet")
    description = _(u"This portlet displays tag information.")
