from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.portlets.portlets.navigation import Renderer as _Renderer
from zope.component import getMultiAdapter

class Renderer(_Renderer):

    _template = ViewPageTemplateFile('templates/navigation.pt')
    recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')

    def heading_link_target(self):

        nav_root = self.getNavRoot()

        # Root content item gone away or similar issue
        if not nav_root:
            return None

        # Go to the item /view we have chosen as root item
        return nav_root.absolute_url()

    @property
    def bottomLevel(self):
        return self.data.bottomLevel or 0

    def createNavTree(self, level=1, bottomLevel=None):

        data = self.getNavTree()

        if not bottomLevel:
            bottomLevel = self.bottomLevel

        if bottomLevel < 0:
            # Special case where navigation tree depth is negative
            # meaning that the admin does not want the listing to be displayed
            return self.recurse([], level=level, bottomLevel=bottomLevel)
        else:
            return self.recurse(children=data.get('children', []), level=level,
                                bottomLevel=bottomLevel)

    def getNavTree(self, _marker=None):
        if _marker is None:
            _marker = []

        context = aq_inner(self.context)

        # Full nav query, not just the tree for 'this' item
        queryBuilder = SitemapQueryBuilder(self.data.navigation_root())
        query = queryBuilder()

        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        # Add explicit path to query, since the sitemap query uses the root of
        # the site
        nav_root = self.getNavRoot()

        if nav_root:
            query['path'] = {
                'query' : "/".join(nav_root.getPhysicalPath()),
                'depth' : self.bottomLevel
            }

        return buildFolderTree(
            context,
            obj=context,
            query=query,
            strategy=strategy
        )

    def link_class(self, level, children):
        if level > 2:
            return ''

        if children:
            return 'd-none d-lg-block'

        return ''