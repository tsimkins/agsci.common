from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.app.layout.viewlets.common import PathBarViewlet as _PathBarViewlet
from plone.app.layout.viewlets.common import TitleViewlet as _TitleViewlet
from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from plone.dexterity.utils import getAdditionalSchemata
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from plone import api
from zope.component import getUtility, queryUtility, getMultiAdapter, queryMultiAdapter
from zope.component.hooks import getSite
from plone.app.contenttypes.interfaces import INewsItem
from plone.event.interfaces import IEvent
from plone.memoize.instance import memoize

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import json
import untangle

from agsci.common.content.check import TileLinksCheck
from agsci.common.interfaces import ICollegeHomepage
from agsci.common.utilities import ploneify, localize
from agsci.common import object_factory
from agsci.common.content.behaviors.leadimage import LeadImage
from agsci.common.content.check import getValidationErrors
from agsci.common.content.person.person import IPerson

try:
    from html import escape
except ImportError:
    from cgi import escape

try:
    from plone.protect.utils import addTokenToUrl
except ImportError:
    def addTokenToUrl(x):
        return x

class ViewletBase(_ViewletBase):

    @property
    def site(self):
        return getSite()

    @property
    def registry(self):
        return getUtility(IRegistry)

    @property
    def portal_url(self):
        return self.context.portal_url()

    def normalize(self, _):
        normalizer = queryUtility(IIDNormalizer)
        return normalizer.normalize(_)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def anonymous(self):
        return api.user.is_anonymous()

    @property
    def is_default_page(self):
        # Determine if we're the default page

        parent = self.context.aq_parent

        try:
            parent_default_page_id = parent.getDefaultPage()
        except AttributeError:
            parent_default_page_id = ''

        return (self.context.id == parent_default_page_id)

class LogoViewlet(ViewletBase):
    pass

class NavigationViewlet(ViewletBase):

    xml_file = '++resource++agsci.common/configuration/navigation.xml'

    def get_paths(self):
        results = self.portal_catalog.searchResults({
            'object_provides' : [
                'plone.dexterity.interfaces.IDexterityContent',
                'Products.PloneFormGen.interfaces.form.IPloneFormGenForm',
            ]
        })

        site_path = "/".join(self.site.getPhysicalPath())

        return dict([(self.normalize_path(x.getPath()[len(site_path):]), True) for x in results])

    def update(self):
        super(NavigationViewlet, self).update()
        self.paths = self.get_paths()

    def label(self, title=''):
        return "-".join([ploneify(self.nav_id), ploneify(title)])

    def hidden(self, item):
        _ = item['hidden']
        return _ and isinstance(_, (str, unicode)) and _.lower().strip() == 'true'

    def type(self, item):
        _ = item['type']

        if _ and isinstance(_, (str, unicode)):
            return _.lower().strip()

        return 'nav'

    def parse_url(self, url, strip_slash=True):
        parsed_url = urlparse(url.strip())

        domain = parsed_url.netloc
        path = parsed_url.path
        scheme = parsed_url.scheme

        if strip_slash:
            if path.endswith('/'):
                path = path[:-1]

        return (scheme, domain, path)

    def link_class(self, item):

        url = self.get_link(item)

        if url:
            if self.is_external_link(url) or self.is_valid_internal_path(url):
                    return 'valid'

        return 'invalid'

    def is_valid_internal_path(self, url):
        path = self.get_internal_path(url)
        return self.paths.has_key(path)

    def get_link(self, item):

        try:
            return item.link.cdata
        except AttributeError:
            pass

    def is_external_link(self, url):
        (scheme, domain, path) = self.parse_url(url)

        # If we have a domain, it's external
        return not not domain

    def normalize_path(self, path):

        if path.startswith('/'):
            path = path[1:]

        if path.endswith('/'):
            path = path[:-1]

        return path

    def get_internal_path(self, url):

        (scheme, domain, path) = self.parse_url(url)

        return self.normalize_path(path)

    def get_internal_url(self, url):

        path = self.get_internal_path(url)

        return '%s/%s' % (self.portal_url, path)

    def link(self, item):

        url = self.get_link(item)

        if url:

            if self.is_external_link(url):
                return url

            return self.get_internal_url(url)

        return ""

    @property
    def config(self):

        resource = self.site.restrictedTraverse(self.xml_file)
        xml = untangle.parse(resource.context.path)
        return xml.config

    @property
    def nav(self):

        for nav in self.config.nav:
            if nav['id'] == self.nav_id:
                return nav

    @property
    def department_id(self):
        _ = self.registry.get('agsci.common.department_id', None)
        
        if _ in [
            'abe', 'aese', 'animalscience', 'ecosystems', 'ento', 
            'foodscience', 'plantpath', 'plantscience', 'vbs'
        ]:
            return safe_unicode(_).encode('utf-8')
        
    @property
    def is_department(self):
        return not not self.department_id

class PrimaryNavigationViewlet(NavigationViewlet):

    nav_id = 'primary'

class AudienceNavigationViewlet(NavigationViewlet):

    nav_id = 'audience'

class DepartmentNavigationViewlet(NavigationViewlet):
    
    @property
    def xml_file(self):
        return '++resource++agsci.common/configuration/navigation-%s.xml' % self.department_id

class PrimaryDepartmentNavigationViewlet(DepartmentNavigationViewlet):

    nav_id = 'primary'
    
    @property
    def nav(self):
        nav = super(PrimaryDepartmentNavigationViewlet, self).nav
        return nav

class AudienceDepartmentNavigationViewlet(DepartmentNavigationViewlet):

    nav_id = 'audience'

class SocialFooterViewlet(NavigationViewlet):

    xml_file = '++resource++agsci.common/configuration/social.xml'

    nav_id = 'social'

class FooterLinksViewlet(NavigationViewlet):

    xml_file = '++resource++agsci.common/configuration/footer.xml'

    nav_id = 'links'

    @property
    def year(self):
        return datetime.now().year

class FooterContactViewlet(FooterLinksViewlet):

    nav_id = 'contact'

class CSSViewlet(ViewletBase):

    edit_permissions = [
        'manage-portal',
        'manage-schemata',
        'modify-portal-content',
        'add-portal-content',
        'delete-objects',
        'portlets-manage-portlets',
        'list-folder-contents',
        'plone-site-setup-editing',
        'plone-site-setup-filtering',
        'plone-site-setup-imaging',
        'plone-site-setup-language',
        'plone-site-setup-mail',
        'plone-site-setup-markup',
        'plone-site-setup-navigation',
        'plone-site-setup-overview',
        'plone-site-setup-search',
        'plone-site-setup-security',
        'plone-site-setup-site',
        'plone-site-setup-themes',
        'plone-site-setup-tinymce',
        'plone-site-setup-types',
        'plone-site-setup-users-and-groups',
        'sharing-page-delegate-roles'
    ]

    @property
    def permissions(self):

        # permissions required. Useful to theme frontend and backend
        # differently

        view = self.view

        permissions = []

        if not getattr(view, '__ac_permissions__', tuple()):
            permissions = ['none']

        for permission, roles in getattr(view, '__ac_permissions__', tuple()):
            permissions.append(self.normalize(permission))

        return permissions

    @property
    def mosaic_enabled(self):
        additional_schemata = getAdditionalSchemata(portal_type=self.context.portal_type)
        if ILayoutAware in additional_schemata:
            if hasattr(self.context, 'getLayout'):
                return self.context.getLayout() in ['layout_view',]

    @property
    def editing_mosaic(self):
        return self.editing and self.mosaic_enabled

    @property
    def editing(self):
        return any([x in self.permissions for x in self.edit_permissions])

class JavaScriptViewlet(ViewletBase):

    @property
    def faceted_enabled(self):
        return IFacetedNavigable.providedBy(self.context)

class PathBarViewlet(_PathBarViewlet):
    index = ViewPageTemplateFile('templates/path_bar.pt')

class LeadImageViewlet(ViewletBase):

    @property
    def adapted(self):
        return LeadImage(self.context)

    @property
    def lightbox_url(self):
        return '%s/@@images/image/large' % self.context.absolute_url()

    @property
    def show_image(self):
        return self.adapted.has_image and self.adapted.image_show

    @property
    def klass(self):
        if self.adapted.image_full_width:
            return 'mb-4 px-0'

        return 'mb-4 ml-lg-3 float-lg-right col-lg-6 px-0'

class DataCheckViewlet(ViewletBase):

    def data(self):
        return getValidationErrors(self.context)

    def post_url(self):
        url = '%s/@@rescan' % self.context.absolute_url()

        return addTokenToUrl(url)

class StructuredDataViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/structured-data.pt')

    @property
    def image(self):
        # Check for item image
        adapted = LeadImage(self.context)

        if adapted.has_image:
            return '%s/@@images/image' % self.context.absolute_url()

    def data(self):

        context = self.context

        data = {}

        if ICollegeHomepage.providedBy(self.context):
            data = {
                    '@context': 'http://schema.org',
                    '@type': 'EducationalOrganization',
                    'address': {    '@type': 'PostalAddress',
                                    'addressLocality': 'University Park',
                                    'addressRegion': 'PA',
                                    'postalCode': '16802',
                                    'streetAddress': 'Penn State University'},
                    'logo': 'https://agsci.psu.edu/psu-agsciences-logo.png',
                    'name': 'Penn State College of Agricultural Sciences',
                    'sameAs': [
                        'https://www.facebook.com/agsciences',
                        'https://www.twitter.com/agsciences',
                        'https://plus.google.com/+PennStateAgSciences',
                        'https://instagram.com/agsciences',
                        'https://www.linkedin.com/company/penn-state-college-of-agricultural-sciences',
                        'https://www.youtube.com/psuagsciences',
                        'https://en.wikipedia.org/wiki/Penn_State_College_of_Agricultural_Sciences'],
                    'telephone': '+1-814-865-7521',
                    'url': 'https://agsci.psu.edu'
                    }

        elif IEvent.providedBy(context):

            data = {
                    '@context': 'http://schema.org',
                    '@type': 'Event',
                    'name': context.Title(),
                    'description' : context.Description(),
                    'startDate' : localize(context.start).isoformat(),
                    'endDate' : localize(context.end).isoformat(),
                    'url' : context.absolute_url(),
                    'location' : {
                        "@type" : "Place",
                        "address" : getattr(context, 'location', ''),
                        "name" : getattr(context, 'location', ''),
                    }
            }

        elif INewsItem.providedBy(context):

            data = {
                    '@context': 'http://schema.org',
                    '@type': 'Article',
                    'headline': context.Title(),
                    'description' : context.Description(),
                    'datePublished' : localize(context.effective()).isoformat(),
                    'url' : context.absolute_url(),
            }

        elif IPerson.providedBy(context):

            # Job Title
            job_titles = getattr(context, 'job_titles', [])

            if job_titles:
                job_title = job_titles[0]
            else:
                job_title = ""

            # Email
            email = getattr(context, 'email', '')

            # Name
            (first_name, middle_name, last_name) = [getattr(context, x, '') for x in ('first_name', 'middle_name', 'last_name')]

            # Address
            street_address = getattr(context, 'street_address', [])

            if street_address:
                street_address = [x for x in street_address if x]
                street_address = ', '.join(street_address)

            city = getattr(context, 'city', '')
            state = getattr(context, 'state', '')
            zip_code = getattr(context, 'zip_code', '')

            # Phone
            phone_number = getattr(context, 'phone_number', '')

            data = {
                    '@context': 'http://schema.org',
                    '@type': 'Person',
                    'url' : context.absolute_url(),
                    'email' : email,
                    'givenName' : first_name,
                    'additionalName' : middle_name,
                    'familyName' : last_name,
                    'telephone' : phone_number,
                    'jobTitle' : job_title,
                    'workLocation' : {
                        '@type' : 'PostalAddress',
                        'addressCountry' : 'US',
                        'addressLocality' : city,
                        'addressRegion' : state,
                        'postalCode' : zip_code,
                        'streetAddress' : street_address,
                    }
            }

        data['image'] = self.image

        if data:
            return json.dumps(data, indent=4)

class TitleViewlet(ViewletBase, _TitleViewlet):

    def update(self):
        pass

    @property
    def org_title(self):
        for _ in self.context.aq_chain:

            org_title = _.getProperty('org_title', None)

            if org_title:
                return org_title

            if IPloneSiteRoot.providedBy(_):
                break

    @property
    @memoize
    def site_title_data(self):

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')

        portal_title = portal_state.navigation_root_title()

        _ = [self.page_title, portal_title, self.org_title]
        _ = [x for x in _ if x]
        _ = [escape(safe_unicode(x)) for x in _]

        items = sorted(set(_), key=lambda x: _.index(x))

        return items

    @property
    def site_title(self):
        return self.sep.join(self.site_title_data)

class OpenGraphViewlet(TitleViewlet):

    # FB config
    fbadmins = ','.join(['100001031380608', '9370853', '100003483428817'])
    fbappid = '374493189244485'
    fbpageid = '53789486293'

    def get_image_info(self, context=None):

        if not context:
            context = self.context

        # Check for item image
        adapted = LeadImage(context)

        if adapted.has_image:
            return ('%s/@@images/image' % self.context.absolute_url(), adapted.image_format)

        return (None, None)

    @property
    def url(self):

        if self.is_default_page:
            return self.context.aq_parent.absolute_url()

        return self.context.absolute_url()

    def update(self):

        # Assign image URL and mime type
        image_url = image_mime_type = ''

        # Look up through the acquisition chain until we hit a Plone site
        for _ in self.context.aq_chain:
            if IPloneSiteRoot.providedBy(_):
                break

            (image_url, image_mime_type) = self.get_image_info(_)

            if image_url:
                break

        # Fallback
        if not image_url:
            image_url = "%s/++resource++agsci.common/assets/images/social-media-site-graphic.png" % self.context.portal_url()

        (self.fb_image, self.link_mime_type) = (image_url, image_mime_type)

        self.link_metadata_image = self.fb_image

        # FB Titles
        titles = self.site_title_data

        if len(titles) == 3:
            self.fb_site_name = u'%s (%s)' % tuple(titles[1:3])
            self.fb_title = u'%s (%s)' % tuple(titles[0:2])

        elif len(titles) == 2:
            self.fb_title = self.fb_site_name = u'%s (%s)' % tuple(titles[0:2])

        else:
            self.fb_title = self.fb_site_name = titles[0]

class TileLinksViewlet(ViewletBase):

    @property
    def check(self):
        return TileLinksCheck(self.context)

    def check_link(self, link):
        return self.check.check_link(link)

    @property
    @memoize
    def links(self):
        return self.check.value()

class CourseSyllabusViewlet(ViewletBase):
    pass

class CourseSyllabusDigitalViewlet(CourseSyllabusViewlet):
    pass