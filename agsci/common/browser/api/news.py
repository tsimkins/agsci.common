from DateTime import DateTime

from agsci.common.constants import DEFAULT_TIMEZONE

from . import JSONDumpView

class TaggedNewsFeedView(JSONDumpView):

    @property
    def path(self):
        return '/'.join(self.site.news.getPhysicalPath())

    @property
    def news_items(self):

        results = self.portal_catalog.searchResults({
            'portal_type' : 'News Item',
            'path' : self.path,
            'SearchText' : 'psu.edu',
            'sort_on' : 'effective',
            'sort_order' : 'descending',
            'created' : {
                'range' : 'min',
                'query' : DateTime() - 365,
            }
        })

        for r in results:

            if isinstance(r.Subject, (list, tuple)) and r.Subject:
                    yield r

    @property
    def data(self):

        site_path = '/'.join(self.site.getPhysicalPath())

        # Return value
        data = []

        for r in self.news_items:

            o = r.getObject()

            link = getattr(o.aq_base, 'article_link', None)

            data.append({
                'getId' : r.getId,
                'path' : r.getPath()[len(site_path):],
                'Subject' : r.Subject,
                'link' : link,
                'title' : r.Title,
                'summary_detail' : {
                    'value' : r.Description,
                },
                'effective' : r.effective.ISO8601(),
                'has_lead_image' : not not r.hasLeadImage,
            })

        return data

class UntaggedNewsFeedView(TaggedNewsFeedView):

    @property
    def news_items(self):

        results = self.portal_catalog.searchResults({
            'Type' : 'News Item',
            'path' : self.path,
            'effective' : {
                'range' : 'min',
                'query' : DateTime() - 31,
            },
            'sort_on' : 'effective',
            'sort_order' : 'reverse'
        })

        for r in results:

            if r.Subject:
                if any([x.startswith('department-') for x in r.Subject]):
                    continue
                if any([x.startswith('news-extension') for x in r.Subject]):
                    continue

            o = r.getObject()

            article_link = getattr(o.aq_base, 'article_link', None)

            if article_link and 'www.psu.edu/news' in article_link:
                yield r