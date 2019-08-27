from AccessControl import ClassSecurityInfo
from Acquisition import aq_acquire, aq_inner
from bs4 import BeautifulSoup
from DateTime import DateTime
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from urlparse import urljoin, urlparse, urlunparse
from zope.component import getUtility, getMultiAdapter
from zope.interface import implements, Interface
from zope.security import checkPermission
from Products.CMFPlone.utils import safe_unicode
from plone.app.contenttypes.interfaces import INewsItem, ILink, ICollection
from urllib import quote, urlencode
from zope.intid.interfaces import IIntIds
from z3c.relationfield.event import addRelations, _relations
from z3c.relationfield.relation import RelationValue

import premailer
import re

from agsci.common.content.blog import IBlog
from agsci.common.content.newsletter import INewsletter

from .. import BaseView

class NewsletterView(BaseView):

    interfaces = [
        INewsItem,
        ILink,
    ]

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.currentDate = DateTime()
        self.config = self.getConfig()

    def hasLeadImage(self):
        return not not self.bodyTag()

    @property
    def canEdit(self):
        try:
            return checkPermission('cmf.ModifyPortalContent', self.context)
        except:
            return False

    def getBodyText(self):
        text = getattr(self.context, 'text', None)

        if text and hasattr(text, 'output'):
            return text.output

    def tag(self, obj, css_class='tileImage', scale='thumb'):
        return '' # This will be item image

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def is_enabled(self, item):

        enabled_items = self.config['enabled']

        if enabled_items:
            return item.UID in enabled_items
        else:
            return self.anonymous

    def is_spotlight(self, item):
        return item.UID in self.config['spotlight']

    def showItem(self, item, item_type='enabled'):
        if item_type=='spotlight':
            return self.is_spotlight(item)
        elif self.is_enabled(item):
            return not self.is_spotlight(item)
        else:
            return not self.anonymous

    @property
    def config_show_summary(self):
        return self.config['show_summary']

    @property
    def show_summary(self):
        show_summary = self.config_show_summary

        if show_summary == 'yes':
            return True
        elif show_summary == 'no':
            return False
        else:
            return len(self.enabled_items) >= 5

    @property
    def target(self):
        target = getattr(self.context, 'target', None)

        if target and hasattr(target, 'to_object'):
            target_object = target.to_object

            if ICollection.providedBy(target_object):
                return target_object

    def get_target_uid(self, target):
        if target and hasattr(target, 'to_object'):
            target_object = target.to_object

            if any([x.providedBy(target_object) for x in self.interfaces]):
                return target_object.UID()

    def getConfig(self):
        value = getattr(self.context, 'value', [])

        if not value:
            value = []

        _ = {}

        _['enabled'] = [
            self.get_target_uid(x.get('target', None))
            for x in value
        ]

        _['spotlight'] = [
            self.get_target_uid(x.get('target', None))
            for x in value if x.get('spotlight', False)
        ]

        _['show_summary'] = getattr(self.context, 'show_summary', 'auto')

        return _

    @property
    def limit(self):
        return getattr(self.context, 'limit', 3)

    @property
    def start_date(self):
        return self.currentDate - 30.5*self.limit

    @property
    def all_items(self):
        target = self.target

        if target:
            _ = target.queryCatalog(batch=False)
            _ = [x for x in _ if x.effective >= self.start_date]
            return _

        return []

    @property
    def enabled_items(self):
        return [
            x for x in self.all_items if
            x.UID in self.config['enabled'] and x.UID not in self.config['spotlight']
        ]

    @property
    def spotlight_items(self):
        return [x for x in self.all_items if x.UID in self.config['spotlight']]

    def setConfig(self, enabled=[], spotlight=[], show_summary='auto'):

        value = []

        intids = getUtility(IIntIds)

        # Make all spotlight articles enabled
        enabled = list(set(enabled).union(set(spotlight)))

        for _ in self.all_items:
            if _.UID in enabled:
                _id = intids.getId(_.getObject())
                _spotlight = _.UID in spotlight
                _target = RelationValue(_id)
                value.append({
                    'target' : _target,
                    'spotlight' : _spotlight,
                })

        setattr(self.context, 'value', value)
        setattr(self.context, 'show_summary', show_summary)

    def getViewOnline(self):

        more_url = getattr(self.context, 'more_url', None)

        if more_url:
            return more_url

        if getattr(self.context, 'hide_view_online', False):

            return None

        parent = self.context.getParentNode()

        if parent.Type() == 'Blog':
            return parent.absolute_url()
        else:
            return self.context.absolute_url()


    @property
    def newsletter_title(self):
        return self.newsletter.Title()

    @property
    def newsletter(self):

        if INewsletter.providedBy(self.context):
            return self.context

        elif IBlog.providedBy(self.context):

            newsletters = self.context.listFolderContents({'Type' : 'Newsletter'})

            if newsletters:

                if len(newsletters) == 1:
                    return newsletters[0]
                else:
                    # By id
                    if 'newsletter' in [x.getId() for x in newsletters]:
                        return self.context['newsletter']
                    else:
                        # Just pick one!
                        return newsletters[0]

    # If we have a @lists.psu.edu listserv, return the listserv name

    @property
    def listserv(self):
        domain = "lists.psu.edu".upper()

        email = getattr(self.newsletter, 'listserv_email', '').upper().strip()

        if email.endswith("@%s" % domain):
            email = email.replace("@%s" % domain, "")
            return email

        return ''

    def listserv_contact_email(self):

        listserv = self.listserv

        if listserv:
            subject = quote('Question about %s' % listserv)
            return '%s-request@lists.psu.edu?Subject=%s' % (listserv, subject)
        else:
            return None

    def listserv_unsubscribe_email(self):

        return self.listserv_subscribe_email(action="unsubscribe")

    def listserv_subscribe_email(self, action="subscribe"):

        listserv = self.listserv

        if listserv:
            return '%s-%s-request@lists.psu.edu' % (listserv, action)
        else:
            return None


    def listserv_url(self):

        listserv = self.listserv

        if listserv:
            return 'http://lists.psu.edu/cgi-bin/wa?SUBED1=%s&A=1' % listserv
        else:
            return None

    @property
    def public_url(self):

        prefix = 'edit.'

        # Calculated URL
        url = self.context.absolute_url()
        parsed_url = urlparse(url)

        if parsed_url.netloc.startswith(prefix):
            return urlunparse(
                [
                    parsed_url.scheme,
                    parsed_url.netloc[len(prefix):],
                    parsed_url.path,
                    '',
                    '',
                    ''
                ]
            )

        # Return the http version of the URL
        return urlunparse(
            [
                'http',
                parsed_url.netloc,
                parsed_url.path,
                '',
                '',
                ''
            ]
        )

class NewsletterModify(NewsletterView):

    security = ClassSecurityInfo()
    security.declareProtected(permissions.ModifyPortalContent, '__call__')

    def __call__(self):
        enabled_items = self.request.form.get('enabled_items', [])
        spotlight_items = self.request.form.get('spotlight_items', [])
        show_summary = self.request.form.get('show_summary', 'auto')

        if not isinstance(enabled_items, list):
            enabled_items = [enabled_items]

        if not isinstance(spotlight_items, list):
            spotlight_items = [spotlight_items]

        self.setConfig(enabled=enabled_items, spotlight=spotlight_items, show_summary=show_summary)

        self.request.response.redirect(self.context.absolute_url())

class NewsletterEmail(NewsletterView):

    def render(self):
        return self.index()

    def getUTM(self, source=None, medium=None, campaign=None, content=None):
        data = {}

        if source:
            data["utm_source"] = source

        if medium:
            data["utm_medium"] = medium

        if campaign:
            data["utm_campaign"] = campaign

        if content:
            data["utm_content"] = content

        return urlencode(data)

    def __call__(self):

        html = self.render()
        html = html.replace('&nbsp;', ' ')

        soup = BeautifulSoup(html, features="lxml")

        for img in soup.findAll('img', {'class' : 'leadimage'}):
            img['hspace'] = 8
            img['vspace'] = 8


        if self.anonymous:

            for a in soup.findAll('a'):
                if 'no_utm' in a.get('class', ''):
                    continue
                klass = [x.replace('utm_', '') for x in a.get('class', []) if x.startswith('utm_')]

                utm_content = None

                if klass:
                    utm_content = klass[0]

                utm  = self.getUTM(source='newsletter', medium='email',
                                   campaign=self.newsletter_title, content=utm_content);

                if '?' in a['href']:
                    a['href'] = '%s&%s' % (a['href'], utm)
                else:
                    a['href'] = '%s?%s' % (a['href'], utm)

        html = premailer.transform(unicode(soup), 'utf-8')

        tags = ['dl', 'dt', 'dd']

        for tag in tags:
            html = html.replace("<%s" % tag, "<div")
            html = html.replace("</%s" % tag, "</div")

        html = re.sub('\s+', ' ', html)
        html = html.replace(' </a>', '</a> ')

        return html

class NewsletterSubscribeView(NewsletterView):

    def page_title(self):
        return "%s Subscription Information" % self.newsletter_title
