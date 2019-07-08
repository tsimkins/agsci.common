from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEventAccessor
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from AccessControl.SecurityManagement import newSecurityManager
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup
from DateTime import DateTime
from time import strptime, strftime
import urllib2
import sys
import re
import requests
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from agsci.common.utilities import localize

class ImportCventView(BrowserView):

    @property
    def site(self):
        return getSite()

    def cvent_events(self, calendar_url, summaryURL):

        def fmt_date(x):
            return DateTime(x.replace("T", ' ') + " US/Eastern")

        results = []

        response = requests.get(calendar_url)

        if response.status_code == 200:

            for _ in response.json():

                _id = _['id']
                _title = _['title']
                _start = fmt_date(_['startDate'])
                _end = fmt_date(_['endDate'])
                _url = self.cvent_summary_url(summaryURL % _id)
                _location = _.get('location', '')

                results.append((_id, _title, _start, _end, _url, _location))

        return results

    def cvent_summary_url(self, url):
        response = requests.get(url)
        return response.url.split('?')[0]

    def __call__(
        self,
        emailUsers=['trs22'],
        cventURL = "http://guest.cvent.com/EVENTS/Calendar/Calendar.aspx?cal=9d9ed7b8-dd56-46d5-b5b3-8fb79e05acaf",
        summaryURL = "http://guest.cvent.com/EVENTS/info/summary.aspx?e=%s",
        conferenceURL="https://agsci.psu.edu/conferences/event-calendar",
        calendar_url="https://agsci.psu.edu/cvent.json",
        owner=None
    ):

        alsoProvides(self.request, IDisableCSRFProtection)

        status = []
        events = []
        cvent_ids = []

        # Get listing of events, and their cventid if it exists
        for _ in self.context.listFolderContents(contentFilter={"Type" : "Event"}):
            cvent_ids.append(_.id)
            cvent_id = _.getProperty('cventid')
            if cvent_id:
                cvent_ids.append(cvent_id)

        for (
            _id,
            _title,
            _start,
            _end,
            _url,
            _location
        ) in self.cvent_events(calendar_url, summaryURL):

            _title = safe_unicode(_title)

            if not cvent_ids.count(_id):
                events.append("<li><a href=\"%s/%s\">%s</a></li>" % (conferenceURL, _id, _title))

                item = createContentInContainer(
                    self.context,
                    "Event",
                    id=_id,
                    title=_title,
                    event_url=_url,
                    location=_location,
                    exclude_from_nav=True,
                    checkConstraints=False
                )

                start_date = localize(DateTime(_start))
                end_date = localize(DateTime(_end))

                acc = IEventAccessor(item)
                acc.start = start_date
                acc.end = end_date

                item.manage_addProperty('cventid', _id, 'string')
                #item.setExcludeFromNav(True)
                #item.setLayout("event_redirect_view")
                item.reindexObject()

                status.append("Created event %s (id %s)" % (_title, _id))

            else:
                status.append("Skipped event %s (id %s)" % (_title, _id))

        if events:
            status.append("Sending email to: %s" % ", ".join(emailUsers))
            mFrom = "do.not.reply@psu.edu"
            mSubj = "CVENT Events Imported: %s" % self.site.getId()
            mTitle = "<p><strong>The following events from cvent have been imported.</strong></p>"
            statusText = "\n".join(events)
            mailHost = self.context.MailHost

            for myUser in emailUsers:
                mTo = "%s@psu.edu" % myUser

                mMsg = "\n".join(["\n\n", mTitle, "<ul>", statusText, "<ul>"])
                mailHost.send(mMsg.encode('utf-8'), mto=mTo, mfrom=mFrom, subject=mSubj)

        status.append("Finished Loading")

        return "\n".join(status)
