from . import JSONDumpView

class TaggedNewsFeedView(JSONDumpView):

    @property
    def news_items(self):
        numeric_ids = [x for x in self.portal_catalog.uniqueValuesFor('id') if x.isdigit()]

        return self.portal_catalog.searchResults({
            'portal_type' : 'News Item',
            'id' : numeric_ids,
            'SearchText' : 'news.psu.edu'
        })

    @property
    def data(self):

        site_path = '/'.join(self.site.getPhysicalPath())

        # Return value
        data = []

        for r in self.news_items:
            subject = r.Subject

            if subject and isinstance(subject, (list, tuple)):

                data.append({
                    'getId' : r.getId,
                    'path' : r.getPath()[len(site_path):],
                    'Subject' : subject,
                })

        data.sort(key=lambda x: x['getId'], reverse=True)

        return data
