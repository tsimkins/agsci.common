from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone.app.blocks.layoutbehavior import ILayoutAware
from plone.app.layout.viewlets.common import PathBarViewlet as _PathBarViewlet
from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from plone.dexterity.utils import getAdditionalSchemata
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone import api
from urlparse import urlparse
from zope.component import queryUtility
from zope.component.hooks import getSite

import untangle

from agsci.common.utilities import ploneify
from agsci.common import object_factory
from agsci.common.content.behaviors.leadimage import LeadImage
from agsci.common.content.check import getValidationErrors

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

class LogoViewlet(ViewletBase):
    pass

class NavigationViewlet(ViewletBase):

    default_url = '/'

    xml_file = '++resource++agsci.common/configuration/navigation.xml'

    def get_paths(self):
        results = self.portal_catalog.searchResults({
            'object_provides' : 'plone.dexterity.interfaces.IDexterityContent'
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
            if not self.is_external_link(url):

                if self.is_valid_internal_path(url):
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

        if not url:
            url = self.default_url

        if self.is_external_link(url):
            return url

        return self.get_internal_url(url)

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

class PrimaryNavigationViewlet(NavigationViewlet):

    nav_id = 'primary'

class AudienceNavigationViewlet(NavigationViewlet):

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
