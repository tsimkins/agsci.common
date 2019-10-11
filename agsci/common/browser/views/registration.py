from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from StringIO import StringIO
from datetime import datetime
from plone import api
from zope.interface import implements, Interface

import HTMLParser
import csv

from agsci.common.utilities import localize, toLocalizedTime

from . import BaseView

class IRegistrationView(Interface):

    def getEventUID(self):
        pass

    def getEventByUID(self):
        pass

    def canViewRegistrations(self, event):
        pass

    def allowRegistration(self, event):
        pass

    def registrationURL(self):
        pass

    def fgFields(self):
        pass

    def getRegistrations(self, show_titles=True):
        pass

    def getAttendeeCount(self):
        pass

    def unescapeHTML(self, e):
        pass

class RegistrationView(BrowserView):

    implements(IRegistrationView)

    @property
    def anonymous(self):
        return api.user.is_anonymous()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def fgFields(self):
        pass

    def toLocalizedTime(self, time, long_format=None, time_only=None,
                        end_time=None, format=None):

        return toLocalizedTime(
            time, long_format=long_format, time_only=time_only,
            end_time=end_time, format=format)

    def getEventUID(self):
        if self.context.portal_type == 'Event':
            return self.context.UID()
        else:
            return self.request.form.get('uid')

    def getEventByUID(self):

        uid = self.getEventUID()

        if uid:
            portal_catalog = getToolByName(self.context, "portal_catalog")
            results = portal_catalog.searchResults({'portal_type' : 'Event', 'UID' : uid})
            if results:
                r = results[0]
                o = r.getObject()
                return o
        return None

    def canViewRegistrations(self, event):
        mt = getToolByName(self.context, 'portal_membership')
        member = mt.getAuthenticatedMember()

        if member.has_role('Event Registration Viewer', event):
            return True
        elif mt.checkPermission('Modify portal content', event):
            return True
        else:
            return False

    def allowRegistration(self, event):
        if not event:
            return False

        if not self.registrationForm:
            return False

        now = localize(datetime.now())

        if hasattr(event, 'free_registration_deadline'):
            registration_deadline = getattr(event, 'free_registration_deadline')
            if registration_deadline:
                if now > localize(registration_deadline):
                    return False

        if now > event.end:
            return False

        if hasattr(event, 'free_registration_attendee_limit'):
            attendee_limit = getattr(event, 'free_registration_attendee_limit')
            if attendee_limit:
                attendeeCount = self.getAttendeeCount()
                if attendeeCount >= attendee_limit:
                    return False

        return True

    def getAttendeeCount(self):
        return len(self.getRegistrations(show_titles=False))

    @property
    def registrationURL(self):
        form = self.registrationForm
        if form:
            return form.absolute_url()
        else:
            return None

    @property
    def registrationForm(self):
        url = getattr(self.context, 'registration_url', None)

        if url:
            url = url.replace('${portal_url}', '')
            if url.startswith('/'):
                url = url[1:]
        else:
            url = "register"

        try:
            return self.context.restrictedTraverse(url)
        except AttributeError:
            return None

    def getRegistrations(self, show_titles=True):
        r_form = self.registrationForm

        if not r_form or 'save-data' not in r_form.objectIds():
            return []

        save_data = r_form['save-data']
        uid = self.getEventUID()

        data = []

        if uid and save_data:
            if show_titles:
                data.append(save_data.getColumnTitles()[1:])
            for r in save_data.getSavedFormInput():
                if r[0] == uid:
                    data.append(r[1:])

        return data

    def unescapeHTML(self, e):
        h = HTMLParser.HTMLParser()
        return h.unescape(safe_unicode(e))


class DownloadCSVView(RegistrationView):
    security = ClassSecurityInfo()
    security.declareProtected(permissions.ModifyPortalContent, '__call__')

    def __call__(self):
        out = StringIO()
        writer = csv.writer(out)
        event = self.getEventByUID()

        registrations = self.getRegistrations()

        if event and self.canViewRegistrations(event) and registrations:
            filename = "%s.csv" % event.getId()
            for r in registrations:
                # Encode fields for CSV writer as utf-8
                r = map(lambda x: safe_unicode(x).encode('utf-8'), r)
                writer.writerow(r)
        else:
           filename = "error.csv"
           writer.writerow(["Error retrieving registration information. Either event does not exist, or you do not have the appropriate permissions."])

        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)


        return out.getvalue()

class RegistrationFormView(BaseView):
    pass