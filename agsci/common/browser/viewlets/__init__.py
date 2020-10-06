from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.layout.viewlets.common import PathBarViewlet as _PathBarViewlet
from plone.app.layout.viewlets.common import TitleViewlet as _TitleViewlet
from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from plone.dexterity.utils import getAdditionalSchemata
from plone.event.interfaces import IEvent
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility, queryUtility, getMultiAdapter, queryMultiAdapter
from zope.component.hooks import getSite

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import json
import untangle

from agsci.common.constants import ASSETS_DOMAIN
from agsci.common.content.behaviors.leadimage import LeadImage
from agsci.common.content.check import TileLinksCheck, TileImagesCheck
from agsci.common.content.check import getValidationErrors
from agsci.common.content.person.person import IPerson
from agsci.common.interfaces import ICollegeHomepage
from agsci.common.utilities import ploneify, localize

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

    XML_CONFIG_DIR = "++resource++agsci.common/configuration"

    @property
    def cache(self):
        return IAnnotations(self.request)

    @property
    def xml_file_path(self):
        return "%s/%s" % (self.XML_CONFIG_DIR, self.xml_file)

    @property
    def site(self):
        return getSite()

    @property
    def registry(self):
        return getUtility(IRegistry)

    @property
    def portal_url(self):
        return self.context.portal_url()

    @property
    def portal_title(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')

        return portal_state.navigation_root_title()

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

    @property
    def template(self):
        return self.view.__name__

    @property
    def search_section(self):

        if hasattr(self.context, 'aq_chain'):

            for o in self.context.aq_chain:

                if IPloneSiteRoot.providedBy(o):
                    break

                _ = getattr(o.aq_base, 'search_section', False)

                if _:
                    return o

    @property
    def search_path(self):
        _ = self.search_section

        if _:
            return '/'.join(_.getPhysicalPath())

    @property
    def search_placeholder(self):
        _ = self.search_section

        if _:
            return u'Search %s' % _.Title()

        return u'Search'

    def is_valid_department_id(self, department_id):

        if department_id:

            if isinstance(department_id, (str, unicode)):

                xml_file = u"%s/navigation-%s.xml" % (
                    safe_unicode(self.XML_CONFIG_DIR),
                    safe_unicode(department_id)
                )

                xml_file = xml_file.encode('utf-8')

                try:
                    config = self.get_xml_config(xml_file)
                except:
                    pass
                else:
                    return True

    @property
    def department_id(self):

        cache_key = 'department_id'

        if cache_key in self.cache:
            return self.cache[cache_key]

        _ = self.registry.get('agsci.common.department_id', None)

        if self.is_valid_department_id(_):
            self.cache[cache_key] = safe_unicode(_).encode('utf-8')
        else:
            self.cache[cache_key] = None

        return self.cache[cache_key]

    @property
    def menu_type(self):
        cache_key = 'menu_type'

        if cache_key in self.cache:
            return self.cache[cache_key]

        config = self.config

        self.cache[cache_key] = self.get_config('type')

        return self.cache[cache_key]

    @property
    def header_type(self):
        cache_key = 'header_type'

        if cache_key in self.cache:
            return self.cache[cache_key]

        config = self.config

        self.cache[cache_key] = self.get_config('header')

        return self.cache[cache_key]

    @property
    def is_department_menu(self):
        return self.menu_type in ('department',)

    @property
    def is_department_header(self):
        return self.header_type in ('department',)

    @property
    def is_department(self):
        return not not self.department_id

    @property
    def use_psu_logo(self):
        cache_key = 'use_psu_logo'

        if cache_key in self.cache:
            return self.cache[cache_key]

        config = self.config

        self.cache[cache_key] = self.get_config('logo') in ('psu',)

        return self.cache[cache_key]

    @property
    def use_extension_logo(self):
        cache_key = 'use_extension_logo'

        if cache_key in self.cache:
            return self.cache[cache_key]

        config = self.config

        self.cache[cache_key] = self.get_config('logo') in ('extension',)

        return self.cache[cache_key]

    @property
    def is_edit(self):
        domain = self.parse_url(self.portal_url)[1]
        return domain.startswith('edit.')

    @property
    def logo_alt(self):

        if self.use_psu_logo:
            return 'Penn State Logo'

        elif self.use_extension_logo:
            return 'Penn State Extension Logo'

        return 'Penn State College of Agricultural Science Logo'

    @property
    def logo_src(self):

        if self.use_psu_logo:
            return 'psu-hor-rgb-rev-2c.png'

        elif self.use_extension_logo:
            return 'psu-ext-1-rgb-rev-2c.png'

        return 'psu-agr-logo-rev-single.png'

    @property
    def logo_class(self):

        if self.use_psu_logo:
            return 'psu-logo'

        elif self.use_extension_logo:
            return 'extension-logo'

        return 'agsci-logo'

    @property
    def logo_href(self):
        if self.use_psu_logo:
            return 'https://www.psu.edu'

        elif self.use_extension_logo:
            return 'https://extension.psu.edu'

        if self.is_edit:
            return 'https://edit.agsci.psu.edu'

        return 'https://agsci.psu.edu'

    def parse_url(self, url, strip_slash=True):
        parsed_url = urlparse(url.strip())

        domain = parsed_url.netloc
        path = parsed_url.path
        scheme = parsed_url.scheme

        if strip_slash:
            if path.endswith('/'):
                path = path[:-1]

        return (scheme, domain, path)

    @property
    def year(self):
        return datetime.now().year

    @property
    def assets_url(self):
        return u"//%s/++resource++agsci.common/assets" % ASSETS_DOMAIN

class NavigationViewlet(ViewletBase):

    @property
    def xml_file(self):

        if self.department_id:
            return 'navigation-%s.xml' % self.department_id

        return 'navigation.xml'

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
        cache_key = 'xml_config|%s' % self.xml_file_path

        if cache_key in self.cache:
            return self.cache[cache_key]

        self.cache[cache_key] = self.get_xml_config(self.xml_file_path)

        return self.cache[cache_key]

    def get_config(self, v, config=None):

        if not isinstance(config, untangle.Element):
            config = self.config

        if hasattr(config, v) and \
           isinstance(config.__dict__[v].cdata, (str, unicode)):
            return config.__dict__[v].cdata.strip()

    def get_xml_config(self, xml_file):
        try:
            resource = self.site.restrictedTraverse(xml_file)
        except:
            raise Exception("Can't find XML config file %s" % xml_file)
        xml = untangle.parse(resource.context.path)
        return xml.config

    @property
    def nav(self):

        for nav in self.config.nav:
            if nav['id'] == self.nav_id:
                return nav

class LogoViewlet(NavigationViewlet):
    pass

class PrimaryNavigationViewlet(NavigationViewlet):

    nav_id = 'primary'

class AudienceNavigationViewlet(NavigationViewlet):

    nav_id = 'audience'

class DepartmentNavigationViewlet(NavigationViewlet):
    pass

class DepartmentAudienceNavigationViewlet(NavigationViewlet):

    @property
    def audience(self):
        return self.get_config('audience-department')

    @property
    def show(self):
        if self.is_department:
            return self.audience in ('department',)

class DepartmentSocialViewlet(DepartmentNavigationViewlet):
    nav_id = 'social'

class DepartmentContactViewlet(DepartmentNavigationViewlet):
    nav_id = 'contact'

class DepartmentFooterViewlet(DepartmentNavigationViewlet):

    @property
    def footer_links(self):
        _ =  FooterLinksViewlet(self.context, self.request, self.manager)
        return _.nav

    @property
    def social_links(self):
        _ =  DepartmentSocialViewlet(self.context, self.request, self.manager)
        return _.nav

    @property
    def contact_links(self):
        _ =  DepartmentContactViewlet(self.context, self.request, self.manager)
        return _.nav

class PrimaryDepartmentNavigationViewlet(DepartmentNavigationViewlet):

    nav_id = 'primary'

    @property
    def nav(self):
        nav = super(PrimaryDepartmentNavigationViewlet, self).nav
        return nav

class AudienceDepartmentNavigationViewlet(DepartmentNavigationViewlet):

    nav_id = 'audience'

class SocialFooterViewlet(NavigationViewlet):

    xml_file = 'social.xml'

    nav_id = 'social'

class FooterLinksViewlet(NavigationViewlet):

    xml_file = 'footer.xml'

    nav_id = 'links'

class FooterContactViewlet(FooterLinksViewlet):

    nav_id = 'contact'

class ModalNavigationViewlet(NavigationViewlet):
    pass

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
        'sharing-page-delegate-roles',
        'cmfeditions-access-previous-versions',
        'modify-constrain-types',
    ]

    edit_templates = [
        'confirm-action',
        'historyview',
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
        is_edit_permissions = any([x in self.permissions for x in self.edit_permissions])
        is_edit_template = self.template in self.edit_templates
        return is_edit_permissions or is_edit_template

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

    def crop_image(self):
        crop_image_view = getMultiAdapter((self.context, self.request), name="crop-image")
        return crop_image_view.allowCrop()

class LeadImageJumbotronViewlet(LeadImageViewlet):

    tile_name = 'agsci.common.tiles.leadimage_jumbotron'

    @property
    def show_image(self):
        return self.adapted.has_image and self.adapted.image_show_jumbotron

    @property
    def img_src(self):
        return self.adapted.img_src

    @property
    def tile(self):
        return queryMultiAdapter((self.context, self.request), name=self.tile_name)

    def render_tile(self):
        tile = self.tile

        if tile:

            tile.set_data({
                'show_title' : True,
                'title' : self.context.Title(),
                'img_src'  : self.img_src,
                'show_breadcrumbs' : True,
            })

            return tile()


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

class SEOViewlet(ViewletBase):

    def noindex(self):

        if hasattr(self.context, 'Type'):
            if self.context.Type() in ['Event',]:

                if hasattr(self.context, 'end'):
                    end = self.context.end

                    if end and isinstance(end, datetime):
                        return DateTime(end) < DateTime()

        if hasattr(self.context, 'expires'):
            expires = self.context.expires()

            if expires and isinstance(expires, DateTime):
                return expires < DateTime()

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

        _ = [self.page_title, self.portal_title, self.org_title]
        _ = [x for x in _ if x]
        _ = [escape(safe_unicode(x)) for x in _]

        items = sorted(set(_), key=lambda x: _.index(x))

        return items

    @property
    @memoize
    def page_title(self):
        if IPloneSiteRoot.providedBy(self.context):
            return {
                'search' : 'Search'
            }.get(self.template, u'')

        return super(TitleViewlet, self).page_title

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

class TileImagesViewlet(ViewletBase):

    @property
    def check(self):
        return TileImagesCheck(self.context)

    def check_image(self, image):
        return self.check.check_image(image)

    @property
    @memoize
    def images(self):
        return self.check.value()

    def getDimensions(self, _=None):
        if isinstance(_, (list, tuple)):
            return " x ".join(['%d' %x for x in _])

    def getSize(self, _=None):
        if isinstance(_, (int, float)):
            return "(%0.1f KB)" % (_/(1024.0))


class CourseSyllabusViewlet(ViewletBase):
    pass

class CourseSyllabusDigitalViewlet(CourseSyllabusViewlet):
    pass

class HistoryViewlet(ViewletBase):
    pass