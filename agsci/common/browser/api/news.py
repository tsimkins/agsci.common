from agsci.common.constants import DEFAULT_TIMEZONE

from . import JSONDumpView

class TaggedNewsFeedView(JSONDumpView):

    @property
    def news_items(self):
        numeric_ids = [x for x in self.portal_catalog.uniqueValuesFor('id') if x.isdigit()]

        return self.portal_catalog.searchResults({
            'portal_type' : 'News Item',
            'id' : numeric_ids,
            'SearchText' : 'news.psu.edu',
            'sort_on' : 'effective',
            'sort_order' : 'descending',
        })

    @property
    def data(self):

        site_path = '/'.join(self.site.getPhysicalPath())

        # Return value
        data = []

        for r in self.news_items:
            subject = r.Subject

            if subject and isinstance(subject, (list, tuple)):

                o = r.getObject()

                link = getattr(o.aq_base, 'article_link', None)

                data.append({
                    'getId' : r.getId,
                    'path' : r.getPath()[len(site_path):],
                    'Subject' : subject,
                    'link' : link,
                    'title' : r.Title,
                    'summary_detail' : {
                        'value' : r.Description,
                    },
                    'effective' : r.effective.ISO8601(),
                })

        return data
