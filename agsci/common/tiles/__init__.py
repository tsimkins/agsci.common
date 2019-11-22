from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.contenttypes.interfaces import ICollection
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.portlets.portlets.navigation import NavtreeStrategy
from plone.app.standardtiles.navigation import NavigationTile as _NavigationTile
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContainer
from plone.memoize.instance import memoize
from plone.namedfile.field import NamedBlobImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.tile import PersistentTile
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

from .interfaces import IBorderTile
from .links import link_factory

from .. import object_factory
from ..content.adapters import LocationAdapter
from ..content.check import uid_re
from ..utilities import toLocalizedTime, getVocabularyTerms, ploneify, toBool
from ..browser.viewlets import PathBarViewlet

class BaseTile(PersistentTile):

    image_scale = None

    __full_width__ = False

    __section_class__ = ''
    __border_top__ = __border_bottom__ = False

    pt = pb = mt = mb = 5

    show_tile = True

    def set_data(self, data):
        self._Tile__cachedData = data

    @property
    def container_width(self):

        if self.__full_width__ or self.get_valid_value('full_width'):
            return 'full'

        return ''

    @property
    def schema(self):
        return ITileDataManager(self).tileType.schema

    @property
    def is_border(self):
        return IBorderTile in self.schema.getBases()

    def get_valid_value(self, field_name):

        schema = self.schema

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

    @property
    def border_top(self):
        return toBool(self.get_valid_value('border_top')) or self.__border_top__

    @property
    def border_bottom(self):
        return toBool(self.get_valid_value('border_bottom')) or self.__border_bottom__

    @property
    def section_class(self):

        _ = []

        if isinstance(self.__section_class__, (str, unicode)):
            _.extend(self.__section_class__.split())

        if self.is_border:

            _.extend([
                'mt-%d' % self.mt,
                'mb-%d' % self.mb,
            ])

            if self.border_top:
                _.extend([
                    'pt-%d' % self.pt,
                    'border-top',
                ])

            if self.border_bottom:
                _.extend([
                    'pb-%d' % self.pb,
                    'border-bottom',
                ])

        return ' '.join(sorted(set(_)))

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
        try:
            _ = ITileDataManager(self)
        except:
            return 'Error'
        else:
            return _.tileType.title

    def can_edit(self):
        if api.user.is_anonymous():
            return False
        current = api.user.get_current()
        return api.user.has_permission(
            'Edit',
            username=current.id,
            obj=self.context)

    @property
    def img_alt(self):
        return self.get_img_alt()

    @property
    def img_src(self):
        return self.get_img_src()

    def get_img_alt(self, serial=None):

        field = 'image_alt'

        if isinstance(serial, int):
            field = '%s_%d' % (field, serial)

        v = self.get_field(field, None)

        if v and isinstance(v, (str, unicode)):
            return v

        return ''

    def get_img_src(self, serial=None, field='image', image_scale=None, full=False):

        if not image_scale:
            image_scale = self.image_scale

        if full:
            image_scale=None

        if isinstance(serial, int):
            field = '%s_%d' % (field, serial)

        img = self.get_field(field, None)

        if img and img.data:
            images = self.publishTraverse(self.request, '@@images')

            try:
                return images.scale(field, scale=image_scale).url
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
    @memoize
    def items(self):
        return self.get_items()

    def get_target_object(self, field='target'):
        target = self.get_field(field)

        if target and hasattr(target, 'to_object'):
            return target.to_object
        elif isinstance(target, (unicode, str)):
            if uid_re.match(target):
                return uuidToObject(target)

    def get_items(self, field='target'):
        target_object = self.get_target_object(field)

        if ICollection.providedBy(target_object):
            return [x for x in target_object.queryCatalog(batch=False)]

        elif IDexterityContainer.providedBy(target_object):
            # Folder Contents
            listing = aq_inner(target_object).restrictedTraverse('@@folderListing', None)

            if listing is None:
                return []

            _ = listing(batch=False)

            # Exclude default page
            _id = target_object.getDefaultPage()

            if _id:
                _ = [x for x in _ if _id != x.getId()]

            return _

    @property
    def more_items_link(self):
        return self.get_more_items_link()

    def get_more_items_link(self, field='target'):
        target_object = self.get_target_object(field)

        if target_object:

            parent = target_object.aq_parent

            if parent and hasattr(parent, 'getDefaultPage'):

                default_page_id = parent.getDefaultPage()
                target_object_id = target_object.getId()

                if default_page_id == target_object_id:
                    return parent.absolute_url()


            return target_object.absolute_url()

    @property
    def site(self):
        return getSite()

    @property
    def portal_url(self):
        return self.site.absolute_url()

    @property
    def is_portlet(self):
        return self.data and isinstance(self.data, dict) and self.data.has_key('__parent__')

    @property
    def links(self):

        for _f in link_factory(self.__name__):

            for _ in _f(self)():
                yield _
    @property
    def images(self):

        for (field_name, field_type) in self.schema.namesAndDescriptions():

            if isinstance(field_type, NamedBlobImage):

                field = self.get_field(field_name, None)

                if field:
                    yield object_factory(
                        name=self.__name__,
                        tile_type=self.tile_type,
                        image=field,
                        thumbnail=self.get_img_src(field=field_name, image_scale='mini'),
                        url=self.get_img_src(field=field_name, full=True),
                        id=self.id,
                    )

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

    __full_width__ = True

    def breadcrumbs(self):
        view = BrowserView(self.context, self.request)
        viewlet = PathBarViewlet(self.context, self.request, view)
        viewlet.update()
        return viewlet.render()

class ShortJumbotronTile(JumbotronTile):
    pass

class CalloutBlockTile(BaseTile):
    pass

class CTATile(BaseTile):

    @property
    def button_width_class(self):
        if self.is_portlet:
            return 'w-100'
        return ''

    @property
    def button_padding_class(self):
        if self.is_portlet:
            return 'px-0 mx-3'
        return ''

class LargeCTATile(BaseTile):
    __full_width__ = True

class KermitTile(BaseTile):
    pass

class MissPiggyTile(BaseTile):
    image_scale = 'large'

    @property
    def image_col_class(self):
        images = [self.get_img_src(x) for x in range(4)]
        image_count = len([x for x in images if x])
        return "col-12 col-lg-12 col-md-%d" % (12/image_count)


class FozzieBearTile(ConditionalTemplateTile):
    __full_width__ = False

    pb = 3

    @property
    def __section_class__(self):
        if self.style in ('light,'):
            return 'px-0'

    @property
    def template(self):
        return 'fozziebear-%s.pt' % self.style

class GonzoTile(ConditionalTemplateTile):

    @property
    def align(self):
        return self.get_valid_value('image_align')

    @property
    def template(self):
        return 'gonzo-%s.pt' % self.align

class RowlfTile(BaseTile):
    __section_class__ = 'journey-preview'
    __border_top__ = __border_bottom__ = True

    image_scale = 'large'

class ScooterTile(ConditionalTemplateTile):
    pb = 3

    def get_items(self):
        items = super(ScooterTile, self).get_items('target')

        if items:
            return items

        return super(ScooterTile, self).get_items('target_container')


    @property
    def template(self):
        return 'scooter-%s.pt' % self.style

class SkeeterTile(ConditionalTemplateTile):

    @property
    def __section_class__(self):

        if self.style in [
            'news-condensed',
        ]:
            return 'container'

        return 'container-fluid'

    @property
    def light_version(self):
        return not not self.get_valid_value('light_version')

    @property
    def filter_tags(self):
        _ = self.get_valid_value('filter_tags')

        if _ and isinstance(_, (list, tuple)):
            return _

    @property
    def filter_public_tags(self):
        _ = self.get_valid_value('filter_public_tags')

        if _ and isinstance(_, (list, tuple)):
            return _

    @property
    def show_tile(self):
        return not not self.items

    @property
    def no_max(self):
        if self.style in ('events',) and self.filter_public_tags:
            return True

    @property
    def max_items(self):

        if self.no_max or self.light_version:
            return 99999

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

                # Get only items with an image
                _ = [x for x in items if x.hasLeadImage]

                if _:
                    return _[0]

                return items[0]

    def get_public_tags(self, o):
        _ = getattr(o, 'public_tags', [])

        if isinstance(_, (list, tuple)):
            return list(_)

        return []

    @property
    def items(self):

        featured = self.featured
        filter_tags = self.filter_tags
        filter_public_tags = self.filter_public_tags

        items = super(SkeeterTile, self).items

        # Filter by tags provided.
        if filter_tags:
            items = [x for x in items if any([y in x.Subject() for y in filter_tags])]

        if filter_public_tags:
            items = [x for x in items if any([y in self.get_public_tags(x) for y in filter_public_tags])]

        if featured:
            items = [x for x in items if x.UID != featured.UID]

        return items[:self.max_items]

    @property
    def template(self):
        return 'skeeter-%s.pt' % self.style

class AnimalTile(BaseTile):

    @property
    def show_image(self):
        return self.get_valid_value('show_image')

    @property
    def klass(self):
        if self.vertical:
            return "card-deck card-deck-%sup mx-2 mb-3" % self.count
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

        def sort_order(_):
            try:
                return _ids.index(_.getId())
            except ValueError:
                return 99999

        return sorted(
            [x.getObject() for x in results],
            key=sort_order
        )

class PepeTheKingPrawnTile(GonzoTile):

    @property
    def template(self):
        return 'pepe_the_king_prawn-%s.pt' % self.align

class RizzoTheRatTile(BaseTile):

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


class YouTubeTile(BaseTile):

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

    @property
    def row_class(self):
        if self.get_field('show_images', None):
            return "col-12 col-md-9 col-xl-7"

        return "col-12"

    @property
    def uuid(self):
        return ploneify(self.data['label'])

class ExploreMoreTile(BaseTile):
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
        nav_root = self.getNavRoot()

        queryBuilder = SitemapQueryBuilder(nav_root)
        query = queryBuilder()

        # Add explicit path to query, since the sitemap query uses the root of
        # the site
        if nav_root:
            query['path'] = {
                'query' : "/".join(nav_root.getPhysicalPath()),
                'depth' : self.data.get('bottomLevel', 3)
            }

        data = dict(self.data)
        data['root_uid'] = data['root']

        strategy = NavtreeStrategy(context, object_factory(**data))

        return buildFolderTree(
            context,
            obj=context,
            query=query,
            strategy=strategy
        )

class SocialMediaTile(BaseTile):

    __section_class__ = 'my-5'

    def get_icon_class(self, _):

        platform = _.platform

        s_icon = {
            'newsletter' : 'far',
        }.get(platform, 'fab')

        p_icon = {
            'instagram' : 'fa-instagram',
            'linkedin' : 'fa-linkedin',
            'newsletter' : 'fa-envelope',
        }.get(platform, 'fa-%s-square' % platform)

        return " ".join([s_icon, p_icon])

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
    pass

class RichTextTile(BaseTile):
    pass

class PullQuoteTile(BaseTile):
    pass
