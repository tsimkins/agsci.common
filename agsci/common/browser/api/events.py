from DateTime import DateTime

from agsci.common.constants import DEFAULT_TIMEZONE

from . import JSONDumpView

class TaggedEventsFeedView(JSONDumpView):

    @property
    def events(self):

        results = self.portal_catalog.searchResults({
            'portal_type' : 'Event',
            'sort_on' : 'start',
            'sort_order' : 'ascending',
            'end' : {
                'range' : 'min',
                'query' : DateTime(),
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

        for r in self.events:

            o = r.getObject()

            link = getattr(o.aq_base, 'event_url', None)

            data.append({
                'getId' : r.getId,
                'path' : r.getPath()[len(site_path):],
                'Subject' : r.Subject,
                'link' : link,
                'title' : r.Title,
                'summary_detail' : {
                    'value' : r.Description,
                },
                'start' : DateTime(r.start).ISO8601(),
                'end' : DateTime(r.end).ISO8601(),
                'effective' : r.effective.ISO8601(),
                'has_lead_image' : not not r.hasLeadImage,
            })

        return data
