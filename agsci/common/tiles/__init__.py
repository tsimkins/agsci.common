from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.tile import PersistentTile
from urlparse import urlparse, parse_qs
from zope.schema import getFields

from .. import object_factory
from ..content.adapters import LocationAdapter
from ..utilities import toLocalizedTime, getVocabularyTerms, ploneify
from ..browser.viewlets import PathBarViewlet

class BaseTile(PersistentTile):

    __type__ = "Base Tile"
    __full_width__ = False

    def set_data(self, data):
        self._Tile__cachedData = data

    @property
    def container_width(self):

        if self.__full_width__ or self.get_valid_value('full_width'):
            return 'full'

        return ''

    def get_valid_value(self, field_name):

        schema = ITileDataManager(self).tileType.schema
        value = self.data.get(field_name)

        if schema:
            field = getFields(schema).get(field_name, None)

            if field:
                if hasattr(field, 'vocabularyName'):
                    vocabulary_name = field.vocabularyName

                    if vocabulary_name:
                        values = getVocabularyTerms(self.context, vocabulary_name)

                        if values:
                            if value in values:
                                return value

                            return field.default

        return value

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
        return self.get_img_src()

    def get_img_src(self, serial=None):

        field = 'image'

        if isinstance(serial, int):
            field = 'image_%d' % serial

        img = self.data.get(field, None)

        if img and img.data:
            images = self.publishTraverse(self.request, '@@images')

            try:
                return images.scale(field).url
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
    def count(self):
        return self.get_valid_value('count')

    @property
    def items(self):
        return self.portal_catalog.searchResults(self.query)

    def get_img_src(self, serial=0):

        image_field = 'image_%d' % serial

        img = self.data.get(image_field, None)

        if img and img.data:
            images = self.publishTraverse(self.request, '@@images')

            try:
                return images.scale(image_field).url
            except AttributeError:
                pass

        return ''

    def get_text(self, serial=0):

        field = 'text_%d' % serial

        if self.data.has_key(field):
            _ = self.data[field]
            if hasattr(_, 'output'):
                return _.output

        return ''

class ConditionalTemplateTile(BaseTile):

    def __call__(self, *args, **kwargs):
        return self.render_template(self, *args, **kwargs)

    @property
    def style(self):
        return self.get_valid_value('style')

    @property
    def render_template(self):
        return ViewPageTemplateFile('templates/%s' % self.template)


class JumbotronTile(BaseTile):

    __type__ = "Jumbotron"
    __full_width__ = True

    def breadcrumbs(self):
        view = BrowserView(self.context, self.request)
        viewlet = PathBarViewlet(self.context, self.request, view)
        viewlet.update()
        return viewlet.render()

class ShortJumbotronTile(JumbotronTile):
    __type__ = "Short Jumbotron"

class CalloutBlockTile(BaseTile):
    __type__ = "Callout Block"

class CTATile(BaseTile):
    __type__ = "Call To Action"
    __full_width__ = True

class LargeCTATile(BaseTile):
    __type__ = "Large CTA"
    __full_width__ = True

class KermitTile(BaseTile):
    __type__ = "Kermit"

class MissPiggyTile(BaseTile):
    __type__ = "Miss Piggy"

class FozzieBearTile(ConditionalTemplateTile):
    __type__ = "Fozzie Bear"
    __full_width__ = False

    @property
    def template(self):
        return 'fozziebear-%s.pt' % self.style

class GonzoTile(ConditionalTemplateTile):
    __type__ = "Gonzo"

    @property
    def align(self):
        return self.get_valid_value('image_align')

    @property
    def template(self):
        return 'gonzo-%s.pt' % self.align

class RowlfTile(BaseTile):
    __type__ = "Rowlf"

class ScooterTile(ConditionalTemplateTile):
    __type__ = "Scooter"

    @property
    def template(self):
        return 'scooter-%s.pt' % self.style

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

        featured_id = self.data.get('featured_id')

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
    def template(self):
        return 'skeeter-%s.pt' % self.style

class AnimalTile(ConditionalTemplateTile):
    __type__ = "Animal"

    @property
    def css_class(self):
        return self.get_valid_value('css_class')

    @property
    def standalone(self):
        return self.get_valid_value('standalone')

    @property
    def klass(self):

        if self.standalone:
            return self.css_class

        return "card-deck card-deck-%sup" % self.count

    def person_view(self, o):
        return o.restrictedTraverse('view')

    @property
    def people(self):

        _ids = [x.get('username', None) for x in self.data.get('value')]

        results = self.portal_catalog.searchResults({
            'Type' : 'Person',
            'getId' : _ids
        })

        return [x.getObject() for x in results]

    @property
    def template(self):
        return 'animal-%s.pt' % self.style

class PepeTheKingPrawnTile(GonzoTile):
    __type__ = "Pepe the King Prawn"

    @property
    def template(self):
        return 'pepe_the_king_prawn-%s.pt' % self.align

class RizzoTheRatTile(BaseTile):
    __type__ = "Rizzo the Rat"

    @property
    def adapted(self):
        # Tricky.  Making the data into an object, and then calling the adapter
        # class directly against it.
        return LocationAdapter(object_factory(**self.data))

    @property
    def street_address(self):
        return self.adapted.street_address

    @property
    def has_address(self):
        return self.adapted.has_address


class StatlerTile(BaseTile):
    __type__ = "Statler"


class YouTubeTile(BaseTile):
    __type__ = "YouTube"

    @property
    def video_id(self):

        url = self.data.get('url', None)

        if url:

            url_object = urlparse(url)
            url_site = url_object.netloc

            # YouTube - grab the 'v' parameter

            if url_site.endswith('youtube.com'):

                params = parse_qs(url_object.query)

                v = params.get('v', None)

                if v:
                    if isinstance(v, list):
                        return v[0]
                    else:
                        return v

            elif url_site.endswith('youtu.be'):

                # URL shortener.  Grabbing the first segment in path
                # as the video id.  Path starts with '/', so we're
                # ignoring the first character.
                v = url_object.path
                return v[1:].split('/')[0]

        return None

    @property
    def wrapper_klass(self):
        _ = ['youtube-video-embed']

        aspect_ratio = self.data.get('video_aspect_ratio', None)

        if aspect_ratio:
            _.append('aspect-%s' % aspect_ratio.replace(':', '-'))

        return " ".join(_)

    @property
    def iframe_url(self):
        video_id = self.video_id

        if video_id:
            return "https://www.youtube.com/embed/%s" % video_id

class DropdownAccordionTile(BaseTile):
    __type__ = "Dropdown Accordion"

    @property
    def row_class(self):
        if self.data.get('show_images', None):
            return "col-12 col-md-9 col-xl-7"
        
        return "col-12"

    @property
    def uuid(self):
        return ploneify(self.data['label'])