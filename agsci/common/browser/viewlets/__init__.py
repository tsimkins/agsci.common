from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from zope.component.hooks import getSite

import untangle

from agsci.common.utilities import ploneify

class ViewletBase(_ViewletBase):

    @property
    def site(self):
        return getSite()
    
class NavigationViewlet(ViewletBase):
    
    def label(self, title=''):
        return ploneify(title)
    
    @property
    def config(self):

        resource = self.site.restrictedTraverse('++resource++agsci.common/navigation/navigation.xml')
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
