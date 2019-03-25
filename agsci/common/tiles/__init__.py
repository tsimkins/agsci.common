from plone import api
from plone import tiles

from base64 import b64encode
from Products.Five.browser import BrowserView

from .. import object_factory
from ..browser.viewlets import PathBarViewlet

class BaseTile(tiles.PersistentTile):

    __type__ = "Base Tile"

    klass = 'base-tile'

    @property
    def tile_type(self):
        return self.__type__

    def can_edit(self):
        if api.user.is_anonymous():
            return False
        current = api.user.get_current()
        return api.user.has_permission(
            'Edit',
            username=current.id,
            obj=self.context)

class JumbotronTile(BaseTile):

    __type__ = "Jumbotron"

    def breadcrumbs(self):
        view = BrowserView(self.context, self.request)
        viewlet = PathBarViewlet(self.context, self.request, view)
        viewlet.update()
        return viewlet.render()

    def background_style(self):
        return "background-image: url(%s);" % self.img_src

    @property
    def img_src(self):
        img = self.data.get('image', None)
        return 'data:image/jpeg;base64,%s' % b64encode(img.data)

class CalloutBlockTile(BaseTile):
    __type__ = "Callout Block"

class CTATile(BaseTile):
    __type__ = "Call To Action"
    
    @property
    def buttons(self):
        v = self.data.get('value', [])
        return [object_factory(**x) for x in v]