from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from zope.component.hooks import getSite

import untangle

from agsci.common.utilities import ploneify
from agsci.common import object_factory

class ViewletBase(_ViewletBase):

    @property
    def site(self):
        return getSite()

class NavigationViewlet(ViewletBase):

    xml_file = '++resource++agsci.common/configuration/navigation.xml'

    def label(self, title=''):
        return "-".join([ploneify(self.nav_id), ploneify(title)])

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