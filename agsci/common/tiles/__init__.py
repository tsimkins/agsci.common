from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.contenttypes.interfaces import ICollection
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.standardtiles.navigation import NavigationTile as _NavigationTile
from plone.app.textfield.value import RichTextValue
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.tile import PersistentTile
from urlparse import urlparse, parse_qs
from zope.component import getMultiAdapter, getUtility
from zope.component.hooks import getSite
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory

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
        ###
        value = self.get_field(field_name)

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

        img = self.get_field(field, None)

        if img and img.data:
            images = self.publishTraverse(self.request, '@@images')

            try:
                return images.scale(field).url
            except AttributeError:
                pass

        return ''

    def background_style(self):
        return "background-image: url(%s);" % self.img_src

    def get_field(self, field, default=None):
        if hasattr(self.data, field):
            return getattr(self.data, field, default)
        else:
            return self.data.get(field, default)

    @property
    def value(self):
        return self.get_field('value', default=[])

    @property
    def values(self):
        return [object_factory(**x) for x in self.value]

    @property
    def count(self):
        return self.get_valid_value('count')

    @property
    def items(self):
        target = self.get_field('target')

        if target and hasattr(target, 'to_object'):
            target_object = target.to_object

            if ICollection.providedBy(target_object):
                return [x for x in target_object.queryCatalog()]

    @property
    def site(self):
        return getSite()

    @property
    def portal_url(self):
        return self.site.absolute_url()

    @property
    def is_portlet(self):
        return self.data and isinstance(self.data, dict) and self.data.has_key('__parent__')

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
    __type__ = "Call To Action (Buttons)"
    __full_width__ = True

    @property
    def button_width_class(self):
        if self.is_portlet:
            return 'w-75'
        return ''

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
            'pages' : 4,
            'news' : 3,
        }.get(self.style, 4)

    @property
    def news_items_class(self):
        if self.is_portlet:
            return "col-12 border-top px-0"
        return "col-12 col-lg-4 border-top px-0"

    @property
    def event_items_count(self):
        if self.is_portlet:
            return 1
        return 4

    @property
    def page_items_count(self):
        if self.is_portlet:
            return 1
        return 3

    @property
    def page_items_cols(self):
        if self.is_portlet:
            return 12
        return 6

    @property
    def page_items_border(self):
        if self.is_portlet:
            return 'border-top'
        return ''

    # Calculates a featured item, otherwise uses the first one.
    # Returns a brain
    @property
    def featured(self):

        # "Tiles as portlets" never have featured items
        if not self.is_portlet:
            items = super(SkeeterTile, self).items

            featured_id = self.get_field('featured_id')

            if featured_id:
                featured_id = featured_id.strip()

                _ = [x for x in items if x.getId() == featured_id]

                if _:
                    return _[0]

            # News always has a featured item
            if items and self.style in ('news',):
                return items[0]

    @property
    def items(self):
        featured = self.featured

        items = super(SkeeterTile, self).items

        if featured:
            items = [x for x in items if x.UID != featured.UID]

        return items[:self.max_items]
    @property
    def template(self):
        return 'skeeter-%s.pt' % self.style

class AnimalTile(BaseTile):
    __type__ = "Person"

    @property
    def klass(self):
        return "card-deck card-deck-%sup" % self.count

    @property
    def vertical(self):
        return self.get_field('style') in ('vertical',)

    @property
    def people(self):

        _ids = [x.get('username', None) for x in self.value]

        results = self.portal_catalog.searchResults({
            'Type' : 'Person',
            'getId' : _ids,
            'sort_on' : 'sortable_title',
        })

        return [x.getObject() for x in results]

class PepeTheKingPrawnTile(GonzoTile):
    __type__ = "Pepe the King Prawn"

    @property
    def template(self):
        return 'pepe_the_king_prawn-%s.pt' % self.align

class RizzoTheRatTile(BaseTile):
    __type__ = "Office Address"

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


class StatlerTile(CTATile):
    __full__width = False
    __type__ = "Call To Action (Blocks)"


class YouTubeTile(BaseTile):
    __type__ = "YouTube"

    @property
    def video_id(self):

        url = self.get_field('url', None)

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

        aspect_ratio = self.get_field('video_aspect_ratio', None)

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
        if self.get_field('show_images', None):
            return "col-12 col-md-9 col-xl-7"

        return "col-12"

    @property
    def uuid(self):
        return ploneify(self.data['label'])

class ExploreMoreTile(BaseTile):
    __type__ = "Explore More"
    __full_width__ = True

class NavigationTile(_NavigationTile):

    recurse = ViewPageTemplateFile('../portlets/templates/navigation_recurse.pt')

    @property
    def heading_link_target(self):

        nav_root = self.getNavRoot()

        # Root content item gone away or similar issue
        if not nav_root:
            return None

        # Go to the item /view we have chosen as root item
        return nav_root.absolute_url()

    def link_class(self, level, children):
        if level > 2:
            return ''

        if children:
            return 'd-none d-lg-block'

        return ''

    def getNavTree(self, _marker=None):
        if _marker is None:
            _marker = []

        context = aq_inner(self.context)

        # Full nav query, not just the tree for 'this' item
        queryBuilder = SitemapQueryBuilder(self.getNavRoot())
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(
            context,
            obj=context,
            query=query,
            strategy=strategy
        )

class SocialMediaTile(BaseTile):
    __type__ = "Social Media"

    def get_icon_class(self, _):

        platform = _.platform

        return {
            'instagram' : 'fa-instagram',
            'linkedin' : 'fa-linkedin',
        }.get(platform, 'fa-%s-square' % platform)

    def get_label(self, _):

        if isinstance(_.label, (str, unicode)) and _.label.strip():
            return _.label.strip()

        # Lookup platform name
        factory = getUtility(IVocabularyFactory, 'agsci.common.tiles.social_media_platform')
        vocabulary = factory(self.context)

        platform = _.platform

        try:
            return vocabulary.getTermByToken(platform).title
        except:
            return platform.title()

class PortletsTile(BaseTile):
    __type__ = "Portlets"