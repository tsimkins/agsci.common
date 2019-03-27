from plone.app.tiles.imagescaling import ImageScale

from plone import api
from plone import tiles

from base64 import b64encode
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .. import object_factory
from ..utilities import toLocalizedTime
from ..browser.viewlets import PathBarViewlet

class BaseTile(tiles.PersistentTile):

    __type__ = "Base Tile"

    query = {
        'Type' : 'Degree',
        'sort_on' : 'sortable_title',
        'sort_order' : 'ascending',
    }

    klass = 'base-tile'

    def date_format(self, time, **kwargs):
        try:
            return toLocalizedTime(time, **kwargs)
        except:
            return 'INVALID DATE OR FORMAT'
    
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

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

    @property
    def img_src(self):
        img = self.data.get('image', None)

        if img and img.data:
            images = self.publishTraverse(self.request, '@@images')

            try:
                return images.scale('image').url
            except AttributeError:
                pass

        return ''

    def background_style(self):
        return "background-image: url(%s);" % self.img_src

    @property
    def values(self):
        v = self.data.get('value', [])
        return [object_factory(**x) for x in v]

    @property
    def items(self):
        return self.portal_catalog.searchResults(self.query)

class ConditionalTemplateTile(BaseTile):

    def __call__(self, *args, **kwargs):
        return self.render_template(self, *args, **kwargs)

    @property    
    def render_template(self):
        return ViewPageTemplateFile('templates/%s' % self.template)


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

class GonzoTile(ConditionalTemplateTile):
    __type__ = "Gonzo"
    
    @property
    def align(self):
        _ = self.data.get('image_align')
        
        if _ == 'left':
            return _
        
        return 'right'

    @property
    def template(self):
        return 'gonzo-%s.pt' % self.align

class RowlfTile(BaseTile):
    __type__ = "Rowlf"

class ScooterTile(ConditionalTemplateTile):
    __type__ = "Scooter"
    
    @property
    def show_description(self):
        return not not self.data.get('show_description')

    @property    
    def template(self):

        if self.show_description:
            return 'scooter-description.pt'

        return 'scooter.pt'

class SkeeterTile(ConditionalTemplateTile):
    __type__ = "Skeeter"

    @property
    def max_items(self):
        return {
            'pages' : 3,
        }.get(self.style, 4)

    @property
    def query(self):
        _ = self.style

        if _ in ('events'):
            return {
                'Type' : 'Event',
                'sort_on' : 'start',
                'sort_order' : 'ascending',
            }

        return super(SkeeterTile, self).query

    # Calculates a featured item, otherwise uses the first one.
    # Returns a brain
    @property
    def featured(self):
        items = super(SkeeterTile, self).items

        featured_id = self.data['featured_id']
        
        if featured_id:
            featured_id = featured_id.strip()
            
            _ = [x for x in items if x.getId ==  featured_id]
            
            if _:
                return _[0]
        
        if items:
            return items[0]

    @property
    def items(self):
        featured = self.featured

        items = super(SkeeterTile, self).items
        
        if featured:
            items = [x for x in items if x.UID != featured.UID]
        
        return items[:(self.max_items-1)]

    @property
    def style(self):
        _ = self.data['style']

        valid = ['news', 'events', 'pages']
        
        if _ in valid:
            return _
        
        return valid[0]

    @property    
    def template(self):
        return 'skeeter-%s.pt' % self.style

class AnimalTile(BaseTile):
    __type__ = "Animal"