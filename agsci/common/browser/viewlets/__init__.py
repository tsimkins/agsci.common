from plone.app.layout.viewlets.common import ViewletBase as _ViewletBase
from zope.component.hooks import getSite

import untangle

from agsci.common.utilities import ploneify

class ViewletBase(_ViewletBase):

    @property
    def site(self):
        return getSite()
    
class PrimaryNavigationViewlet(ViewletBase):
    
    def label(self, title=''):
        return ploneify(title)
    
    @property
    def nav(self):

        resource = self.site.restrictedTraverse('++resource++agsci.common/navigation/primary.xml')
        xml = untangle.parse(resource.context.path)
        return xml.nav