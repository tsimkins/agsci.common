from plone import api
from plone import tiles

from base64 import b64encode
from Products.Five.browser import BrowserView

from .. import object_factory
from ..browser.viewlets import PathBarViewlet

class BaseTile(tiles.PersistentTile):

    klass = 'base-tile'

    def can_edit(self):
        if api.user.is_anonymous():
            return False
        current = api.user.get_current()
        return api.user.has_permission(
            'Edit',
            username=current.id,
            obj=self.context)

class JumbotronTile(BaseTile):
    
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
    pass

class TestTile(BaseTile):

    def item_klass(self):
    
        _ = [
            (4, 'mosaic-width-quarter'),
            (3, 'mosaic-width-third'),
            (2, 'mosaic-width-half'),
        ]
    
        values = [x for x in self.values]
        
        if values:

            value_count = len(values)
            
            for (v,k) in _:
                if not value_count % v:
                    return k

            # Default largest
            if value_count > _[0][0]:
                return _[0][1]
                
        return 'mosaic-width-full'
        
    @property
    def values(self):
        headings = ['title', 'description', 'link'] 

        values = self.data.get('values', [])
        
        if values:

            for _ in values:
                values = [x.strip() for x in _.split('|')]
                kwargs = dict(zip(headings, values))
                yield object_factory(**kwargs)