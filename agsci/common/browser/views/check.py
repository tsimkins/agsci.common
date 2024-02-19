from plone.batching import Batch
from plone.memoize.view import memoize
from zope.component import subscribers

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from agsci.common.content.check import IContentCheck
from . import FolderView

class ContentTypeChecks(object):

    def __init__(self, product_type='', checks=[]):
        self.product_type = product_type
        self.checks = checks

# This view will show all of the automated checks by content type
class EnumerateErrorChecksView(FolderView):

    description = 'All Content'

    show_about = False

    @property
    def results(self):
        return self.portal_catalog.searchResults({
            'path' : '/'.join(self.context.getPhysicalPath()),
            'object_provides' : 'plone.dexterity.interfaces.IDexterityContent',
        })

    def getChecksByType(self):

        # initialize return list
        data = []

        # Search for all of the Atlas Products
        results = self.results

        # Get a unique list of product types
        product_types = set([x.Type for x in results])

        # Iterate through the unique types, grab the first object of that
        # type from the results
        for pt in sorted(product_types):

            # Get a list of all objects of that product type
            products = [x for x in results if x.Type == pt]

            # Grab the first element (brain) in that list
            r = products[0]

            # Grab the object for the brain
            context = r.getObject()

            # Get content checks
            checks = []

            for c in subscribers((context,), IContentCheck):
                if self.show_all or self.getIssueCount(pt, c) > 0:
                    checks.append(c)

            checks.sort(key=lambda x: x.sort_order)

            # Append a new ContentTypeChecks to the return list
            data.append(ContentTypeChecks(pt, checks))

        return data

    @property
    def show_all(self):
        return not not self.request.form.get('all', None)

    @property
    @memoize
    def issueSummary(self):
        data = {}

        results = self.results

        for r in results:
            if r.Type not in data:
                data[r.Type] = {}
            if r.ContentErrorCodes:
                for i in r.ContentErrorCodes:
                    if i not in data[r.Type]:
                        data[r.Type][i] = 0
                    data[r.Type][i] = data[r.Type][i] + 1
        return data

    def getErrorListingURL(self, ptc, c):
        product_type = ptc.product_type
        error_code = c.error_code
        params = urlencode({'Type' : product_type, 'ContentErrorCodes' : error_code})
        return '%s/@@content_check_items?%s' % (self.context.absolute_url(), params)

    def getIssueCount(self, ptc, c):
        if isinstance(ptc, ContentTypeChecks):
            product_type = ptc.product_type
        else:
            product_type = ptc
        error_code = c.error_code
        return self.issueSummary.get(product_type, {}).get(error_code, 0)

class ContentCheckItemsView(EnumerateErrorChecksView):

    description = 'All Content'

    @property
    def query(self):
        return {
            'path' : '/'.join(self.context.getPhysicalPath()),
        }

    @property
    def results(self):
        query = self.query
        query.update(self.request.form)
        query['sort_on'] = 'sortable_title'
        return self.portal_catalog.searchResults(query)

    @property
    def batch(self):
        return Batch(self.results, 99999, start=0)

    @property
    def show_description(self):
        return True

    @property
    def show_image(self):
        return True
