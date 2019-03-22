from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from plone.app.layout.viewlets.common import PathBarViewlet as _PathBarViewlet
from urlparse import urlparse
from zope.component.hooks import getSite
from zope.component import queryUtility

import untangle

from agsci.common.utilities import ploneify
from agsci.common import object_factory

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

class NavigationViewlet(ViewletBase):

    default_url = '/'

    xml_file = '++resource++agsci.common/configuration/navigation.xml'

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

    def link(self, item):

        try:
            url = item.link.cdata
        except AttributeError:
            url = self.default_url

        (scheme, domain, path) = self.parse_url(url)

        # If we have a domain, it's external
        if domain:
            return url

        if path.startswith('/'):
            path = path[1:]

        return '%s/%s' % (self.portal_url, path)

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

class FooterContactViewlet(FooterLinksViewlet):

    nav_id = 'contact'

class CSSViewlet(ViewletBase):

    edit_permissions = [
        'manage-portal',
        'manage-schemata',
        'plone-site-setup-site',
        'modify-portal-content',
        'add-portal-content',
        'portlets-manage-portlets',
        'plone-site-setup-overview',
        'plone-site-setup-users-and-groups',
        'list-folder-contents'
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
    def editing(self):
        return any([x in self.permissions for x in self.edit_permissions])

class JavaScriptViewlet(ViewletBase):

    @property
    def faceted_enabled(self):
        return IFacetedNavigable.providedBy(self.context)


class PathBarViewlet(_PathBarViewlet):
    pass