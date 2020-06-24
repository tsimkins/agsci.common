from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from email.mime.text import MIMEText
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEventAccessor

import requests

from agsci.common.constants import AGSCI_DOMAIN
from agsci.common.utilities import localize
from .. import ImportContentView

# For Cvent URL http://guest.cvent.com/EVENTS/Calendar/Calendar.aspx?cal=9d9ed7b8-dd56-46d5-b5b3-8fb79e05acaf

class ImportCventView(ImportContentView):

    summary_url = "http://guest.cvent.com/EVENTS/info/summary.aspx?e=%s"

    conference_url = "https://edit.agsci.psu.edu/conferences/event-calendar"

    calendar_url = "https://%s/cvent.json" % AGSCI_DOMAIN

    email_users = ['trs22', 'kkw115', 'buh22', 'nmk107', 'sko2']

    @property
    def cvent_events(self):

        def fmt_date(x):
            return localize(DateTime(x.replace("T", ' ') + " US/Eastern"))

        response = requests.get(self.calendar_url, verify=False)

        if response.status_code == 200:

            for _ in response.json():
                _id = _['id']
                _title = _['title']
                _start = fmt_date(_['startDate'])
                _end = fmt_date(_['endDate'])
                _url = self.cvent_summary_url(_id)
                _location = _.get('location', '')

                yield {
                    'id' : _id,
                    'title' : _title,
                    'start' : _start,
                    'end' : _end,
                    'url' : _url,
                    'location' : _location
                }

    def cvent_summary_url(self, cvent_id):
        url = self.summary_url % cvent_id
        response = requests.get(url)
        return response.url.split('?')[0]

    @property
    def existing_cvent_ids(self):
        cvent_ids = []

        # Get listing of events, and their cventid if it exists
        for _ in self.context.listFolderContents(contentFilter={"Type" : "Event"}):
            cvent_ids.append(_.id)
            cvent_id = _.getProperty('cventid')
            if cvent_id:
                cvent_ids.append(cvent_id)

        return cvent_ids

    def create_cvent_event(self, **kwargs):

        item = createContentInContainer(
            self.context,
            "Event",
            id=kwargs['id'],
            title=kwargs['title'],
            event_url=kwargs['url'],
            location=kwargs['location'],
            exclude_from_nav=True,
            checkConstraints=False
        )

        start_date = kwargs['start']
        end_date = kwargs['end']

        acc = IEventAccessor(item)
        acc.start = start_date
        acc.end = end_date

        item.manage_addProperty('cventid', kwargs['id'], 'string')
        item.setLayout("event_redirect_view")
        item.reindexObject()

        return item

    def import_content(self):

        status = []
        events = []
        cvent_ids = self.existing_cvent_ids

        for _ in self.cvent_events:

            _title = safe_unicode(_['title'])
            _id = _['id']

            if not cvent_ids.count(_id):
                events.append("<li><a href=\"%s/%s\">%s</a></li>" % (self.conference_url, _id, _title))

                self.create_cvent_event(**_)

                status.append("Created event %s (id %s)" % (_title, _id))

            else:
                status.append("Skipped event %s (id %s)" % (_title, _id))

        if events:
            status.append("Sending email to: %s" % ", ".join(self.email_users))
            mFrom = "do.not.reply@psu.edu"
            mSubj = "CVENT Events Imported: %s" % self.site.getId()
            mTitle = "<p><strong>The following events from cvent have been imported.</strong></p>"
            statusText = "\n".join(events)
            mailHost = self.context.MailHost

            for myUser in self.email_users:
                mTo = "%s@psu.edu" % myUser

                mMsg = "\n".join(["\n\n", mTitle, "<ul>", statusText, "<ul>"])
                mMsg = MIMEText(mMsg, 'html')

                mailHost.send(mMsg, mto=mTo, mfrom=mFrom, subject=mSubj)

        status.append("Finished Loading")

        return "\n".join(status)