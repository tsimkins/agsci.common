from plone.app.tiles.imagescaling import ImageScale

from plone import api
from plone import tiles

from base64 import b64encode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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

    def img_src_url(self, images):
        try:
            return images.scale('image').url
        except AttributeError:
            return ''

    @property
    def img_src(self):
        img = self.data.get('image', None)

        if img and img.data:
            scale = ImageScale(self, self.request, data=img, fieldname='image')
            return scale.url

    def background_style(self):
        return "background-image: url(%s);" % self.img_src

    @property
    def values(self):
        v = self.data.get('value', [])
        return [object_factory(**x) for x in v]

class JumbotronTile(BaseTile):

    __type__ = "Jumbotron"

    def breadcrumbs(self):
        view = BrowserView(self.context, self.request)
        viewlet = PathBarViewlet(self.context, self.request, view)
        viewlet.update()
        return viewlet.render()

class CalloutBlockTile(BaseTile):
    __type__ = "Callout Block"

class CTATile(BaseTile):
    __type__ = "Call To Action"
    
class KermitTile(BaseTile):
    __type__ = "Kermit"

class MissPiggyTile(BaseTile):
    __type__ = "Miss Piggy"

class FozzieBearTile(BaseTile):
    __type__ = "Fozzie Bear"

class GonzoTile(BaseTile):
    __type__ = "Gonzo"
    
    @property
    def align(self):
        _ = self.data.get('image_align')
        
        if _ == 'left':
            return _
        
        return 'right'

    def __call__(self, *args, **kwargs):
        return self.template(self, *args, **kwargs)

    @property    
    def template(self):
        return ViewPageTemplateFile('templates/gonzo-%s.pt' % self.align)