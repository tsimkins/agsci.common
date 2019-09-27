from eea.facetednavigation.browser.app.query import FacetedQueryHandler
from eea.facetednavigation.caching import ramcache
from eea.facetednavigation.caching import cacheKeyFacetedNavigation
from . import DegreeListingView

class DegreeExplorerFacetedQueryHandler(DegreeListingView, FacetedQueryHandler):

    def criteria(self, sort=False, **kwargs):
        query = self.getQuery()
        faceted_query = super( DegreeExplorerFacetedQueryHandler, self).criteria(sort, **kwargs)
        query.update(faceted_query)
        return query

    @ramcache(cacheKeyFacetedNavigation, dependencies=['eea.facetednavigation'])
    def __call__(self, *args, **kwargs):
        kwargs['batch'] = False
        self.brains = self.query(**kwargs)
        html = self.index()
        return html