from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.portlets.portlets.navigation import Renderer as _Renderer
from zope.component import getMultiAdapter

class Renderer(_Renderer):

    _template = ViewPageTemplateFile('templates/navigation.pt')

    def getNavTree(self, _marker=None):
        if _marker is None:
            _marker = []

        context = aq_inner(self.context)

        # Full nav query, not just the tree for 'this' item
        queryBuilder = SitemapQueryBuilder(self.data.navigation_root())
        query = queryBuilder()

        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        return buildFolderTree(
            context,
            obj=context,
            query=query,
            strategy=strategy
        )