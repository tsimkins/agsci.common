from DateTime import DateTime

from agsci.common.constants import DEFAULT_TIMEZONE

from . import JSONDumpView

class UpdatedPublishedFeedView(JSONDumpView):

    @property
    def path(self):
        return '/'.join(self.context.getPhysicalPath())

    @property
    def days_back(self):
        return 14

    @property
    def items(self):

        results = self.portal_catalog.searchResults({
            'path' : self.path,
            'sort_on' : 'modified',
            'sort_order' : 'descending',
            'modified' : {
                'range' : 'min',
                'query' : DateTime() - self.days_back,
            },
            'review_state' : 'published',
        })

        return results

    def fmt_date(self, _):
        if isinstance(_, DateTime):
            return _.ISO8601()
        return None

    @property
    def data(self):

        site_path = '/'.join(self.site.getPhysicalPath())
        site_id = self.site.getId().replace('.psu.edu', '')

        # Return value
        data = []

        for r in self.items:

            data.append({
                'type' : r.Type,
                'getId' : r.getId,
                'url' : r.getURL(),
                'title' : r.Title,
                'path' : r.getPath()[len(site_path):],
                'description' : r.Description,
                'effective' : self.fmt_date(r.effective),
                'modified' : self.fmt_date(r.modified),
            })

        return data


class PendingReviewFeedView(UpdatedPublishedFeedView):

    @property
    def items(self):

        results = self.portal_catalog.searchResults({
            'path' : self.path,
            'sort_on' : 'effective',
            'sort_order' : 'descending',
            'modified' : {
                'range' : 'min',
                'query' : DateTime() - self.days_back,
            },
            'review_state' : 'pending',
        })

        return results
