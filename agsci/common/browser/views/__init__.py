from Acquisition import aq_base, aq_inner
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.search import Search as _SearchView
from Products.CMFPlone.browser.search import BAD_CHARS, quote, quote_chars
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collections import OrderedDict
from collective.z3cform.datagridfield import DictRow
from jinja2 import Environment, FileSystemLoader
from plone import api
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.dexterity.browser.folder_listing import FolderView as _FolderView
from plone.app.event.browser.event_summary import EventSummaryView as _EventSummaryView
from plone.app.event.browser.event_view import EventView as _EventView
from plone.app.layout.globals.layout import LayoutPolicy as _LayoutPolicy
from plone.app.layout.sitemap.sitemap import SiteMapView as _SiteMapView
from plone.batching import Batch
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.interfaces import IEvent
from plone.memoize.view import memoize
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import getMultiAdapter, getUtility
from zope.interface import implementer, alsoProvides
from zope.publisher.interfaces import IPublishTraverse
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema

from agsci.common import object_factory
from agsci.common.constants import ASSETS_DOMAIN
from agsci.common.content.check import ExternalLinkCheck, TileLinksCheck
from agsci.common.content.degrees import IDegree
from agsci.common.content.major import IMajor
from agsci.common.indexer import degree_index_field
from agsci.common.interfaces import ILocationAdapter
from agsci.common.interfaces import ITagsAdapter
from agsci.common.utilities import get_fields_by_type, toLocalizedTime, \
    getNavigationViewlet

try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite

import json

class BaseView(BrowserView):

    j2_template_base = "++resource++agsci.common.view.j2/"

    image_size = 'large'

    @property
    def site(self):
        return getSite()

    @property
    def object_fields(self):
        portal_type = self.context.portal_type
        return get_fields_by_type(portal_type)

    @property
    def data(self):

        _ = {}

        fields = self.object_fields

        for (i,f) in fields.iteritems():

            if f:

                value = getattr(self.context, i, None)

                value_type = None

                if hasattr(f, 'value_type'):
                    value_type = f.value_type

                is_grid = isinstance(value_type, DictRow)

                if is_grid and isinstance(f, (schema.List, schema.Tuple)):
                    try:
                        value = [object_factory(**x) for x in value]
                    except:
                        value = []

                __ = {
                    'name' : i,
                    'title' : f.title,
                    'value' : value,
                }

                _[i] = object_factory(**__)

        return object_factory(**_)

    def item_image(self, item=None, size='large'):

        if not self.item_has_image(item):
            return None

        if not item:
            item = self.context

        # Is a brain
        if hasattr(item, 'getURL'):
            url = item.getURL()

        elif hasattr(item, 'absolute_url'):
            url = item.absolute_url()

        else:
            url = self.context.absolute_url()

        if size:
            return '%s/@@images/image/%s' % (url, size)

        return '%s/@@images/image' % (url,)

    @property
    def image(self):
        return self.item_image(size=self.image_size)

    def item_date(self, item):
        if hasattr(item, 'effective_date'):
            if item.effective_date:
                return toLocalizedTime(item.effective_date)

    @property
    def show_date(self):
        return getattr(aq_base(self.context), 'show_date', False)

    @property
    def show_description(self):
        return getattr(aq_base(self.context), 'show_description', False)

    @property
    def show_image(self):
        return getattr(aq_base(self.context), 'show_image', False)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal_types(self):
        return getToolByName(self.context, 'portal_types')

    @property
    def anonymous(self):
        return api.user.is_anonymous()

    @property
    def portal_url(self):
        return self.portal.absolute_url()

    def getCurrentUser(self):
        return api.user.get_current()

    def isDefaultPage(self):
        if not hasattr(self.context.aq_parent, 'getDefaultPage'):
            return False

        return (self.context.getId() == self.context.aq_parent.getDefaultPage())

    def item_has_image(self, item=None):

        has_image = False

        if not item:
            item = self.context

        # Is a brain
        if hasattr(item, 'hasLeadImage'):
            has_image = item.hasLeadImage
        else:
            from agsci.common.indexer import hasLeadImage as _hasLeadImage
            has_image = _hasLeadImage(item)()

        return has_image

    def show_item_image(self, item):
        return self.show_image and  self.item_has_image(item)

    def item_class(self, item):
        _ = ['col-12', 'order-sm-1', 'order-2', 'mt-0', 'px-0']

        if self.show_item_image(item):
            _.extend(['col-sm-6 ', 'col-md-8', 'col-xl-9'])

        return " ".join(_)

    def getItemURL(self, item):

        item_type = item.portal_type

        if hasattr(item, 'getURL'):
            item_url = item.getURL()
        else:
            item_url = item.absolute_url()

        if not self.anonymous:
            if item_type in self.use_view_action:
                return item_url + '/view'

        return item_url

    @property
    def use_view_action(self):

        if not self.anonymous:
            registry = getUtility(IRegistry)
            return registry.get('plone.types_use_view_action_in_listings', [])

        return []

    def get_event_date_range(self, context):
        start = context.start
        end = context.end

        whole_day = getattr(context, 'whole_day', False)
        open_end = getattr(context, 'open_end', False)

        if whole_day:

            if open_end:
                return toLocalizedTime(start)

            return toLocalizedTime(start, end_time=end)

        elif open_end:
            return toLocalizedTime(start, long_format=True)

        return toLocalizedTime(start, end_time=end, long_format=True)

    def render_j2(self, template=None, item=None, data=[]):
        resource = self.site.restrictedTraverse(self.j2_template_base)

        loader = FileSystemLoader(resource.context.path)

        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        _template = env.get_template(template)

        return _template.render(view=self, item=item, data=data)

    def publications_html(self, publications=[]):

        if not publications:
            if hasattr(self.context, 'publications') and isinstance(self.context.publications, (list, tuple)):
                publications = self.context.publications

        return self.render_j2(template='publications.j2', data=publications)

    @property
    def assets_url(self):
        return u"//%s/++resource++agsci.common/assets" % ASSETS_DOMAIN

    @property
    def navigation_viewlet(self):
        return getNavigationViewlet()

    @property
    def department_id(self):
        return self.navigation_viewlet.department_id

    def registry(self):
        return getUtility(IRegistry)

    @property
    def enhanced_public_tags(self):
        return not not self.registry.get('agsci.common.enhanced_public_tags')

    def format_tags(self, tags=[]):
        if tags:
            return ", ".join(sorted(tags))

class DegreeListingView(BaseView):

    image_size = None

    def getQuery(self):
        return {'Type' : 'Degree', 'sort_on' : 'sortable_title'}

    def getFolderContents(self):
        return self.portal_catalog.queryCatalog(self.getQuery())

class DegreeView(BaseView):

    def get_target(self, context):
        target = getattr(context, 'target', None)

        if target and hasattr(target, 'to_object'):
            target_object = target.to_object

            if IMajor.providedBy(target_object):
                return target_object.absolute_url()

    @property
    def target(self):
        return self.get_target(self.context)

    @property
    def fields(self):

        fields = [x[1] for x in degree_index_field]

        def sort_order(x):
            try:
                return fields.index(x)
            except ValueError:
                return 99999

        sorted_fields = sorted(IDegree.namesAndDescriptions(), key=lambda x: sort_order(x[0]))

        return [x[1] for x in sorted_fields]

class DegreeCompareView(DegreeView):

    @property
    def degrees(self):

        _ids = self.request.form.get('degree_id', [])

        results = self.portal_catalog.searchResults({
            'Type' : 'Degree',
            'sort_on' : 'sortable_title',
            'getId' : _ids,
        })

        return [x.getObject() for x in results]

class PersonView(BaseView):

    index = ViewPageTemplateFile("templates/person.pt")

    card = False

    @property
    def primary_profile_url(self):
        return getattr(self.context, 'primary_profile_url', None)

    @property
    def is_expired(self):
        return self.context.expires() < DateTime()

    @property
    def show_profile(self):
        return (self.is_expired and not self.anonymous) or not self.is_expired

    @property
    def show_publications(self):
        return not not getattr(self.context, 'show_publications', True)

    @property
    def show_publications_block(self):
        # Always show when logged in
        return self.show_publications or not self.anonymous

    def __call__(self):

        if self.anonymous and self.primary_profile_url and not self.card:

            RESPONSE =  self.request.RESPONSE

            RESPONSE.setHeader(
                'Cache-Control',
                'max-age=0, s-maxage=3600, must-revalidate, public, proxy-revalidate'
            )

            return RESPONSE.redirect(self.primary_profile_url)

        return self.index()

    @property
    def adapted(self):
        return ILocationAdapter(self.context)

    @property
    def name(self):
        return self.context.name_data

    @property
    def job_title(self):
        _ = getattr(self.context, 'job_titles', [])

        if _:
            return _[0]

    @property
    def street_address(self):
        return self.adapted.street_address

    @property
    def has_address(self):
        return self.adapted.has_address

    @property
    def cv_file(self):
        _ = getattr(self.context, 'cv_file', None)

        if _ and hasattr(_, 'contentType') and _.contentType in ('application/pdf'):
                return "%s/@@download/cv_file" % self.context.absolute_url()


class PersonCardView(PersonView):

    card = True
    card_format = 'horizontal'
    border = True
    show_image = False

    @property
    def card_image_class(self):

        if self.card_format in ('vertical',):
            return 'col-12 px-0 mb-2'

        return 'col-12 col-md-5 col-sm-12 px-0'

    @property
    def card_class(self):

        if self.card_format in ('vertical',):

            if self.border:
                return 'card card-short-bio agsci-box-shadow card-vertical html mb-3'

            return 'card card-short-bio card-vertical html mb-2'

        return 'card card-short-bio agsci-box-shadow html'

    @property
    def card_details_class(self):
        if self.card_format in ('vertical',):
            return 'col-12 px-0'

        return 'col-12 col-sm-12 col-md-7 mt-2 mt-md-0 pl-0 px-sm-0 pr-0 pl-md-3 pl-sm-0'

class PersonCardVerticalView(PersonCardView):
    card_format = 'vertical'

class PersonCardImageView(PersonCardView):
    show_image = True

class PersonCardVerticalImageView(PersonCardVerticalView):
    show_image = True

class PersonCardVerticalNoBorderView(PersonCardVerticalView):
    border = False
    show_image = True

class FolderView(_FolderView, BaseView):

    batch_size = 500 # Because pagination *sucks*

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)

        limit_display = getattr(self.request, 'limit_display', None)
        limit_display = int(limit_display) if limit_display is not None else self.batch_size

        b_size = getattr(self.request, 'b_size', None)
        self.b_size = int(b_size) if b_size is not None else limit_display

    def getItemSize(self, item):

        if hasattr(item, 'getObjSize'):
            if hasattr(item.getObjSize, '__call__'):
                return item.getObjSize()
            else:
                return item.getObjSize

    def fileExtensionIcons(self):
        ms_data = ['xls', 'doc', 'ppt']

        data = {
            'xls' : u'Microsoft Excel',
            'ppt' : u'Microsoft PowerPoint',
            'publisher' : u'Microsoft Publisher',
            'doc' : u'Microsoft Word',
            'pdf' : u'PDF',
            'pdf_icon' : u'PDF',
            'text' : u'Plain Text',
            'txt' : u'Plain Text',
            'zip' : u'ZIP Archive',
        }

        for ms in ms_data:
            ms_type = data.get(ms, '')
            if ms_type:
                data['%sx' % ms] = ms_type

        return data

    def getRemoteUrl(self, item):
        if hasattr(item, 'getRemoteUrl'):
            if hasattr(item.getRemoteUrl, '__call__'):
                return item.getRemoteUrl()
            else:
                return item.getRemoteUrl

    def getLinkType(self, url):

        if '.' in url:
            icon = url.strip().lower().split('.')[-1]
            return self.fileExtensionIcons().get(icon, None)

    def getFileType(self, item):

        mimetypes_registry = getToolByName(self.context, 'mimetypes_registry')

        _ = mimetypes_registry.lookup(item.mime_type)

        if _:
            return _[0].name()


    def getItemInfo(self, item):

        if item.portal_type in ['File',]:
            obj_size = self.getItemSize(item)
            file_type = self.getFileType(item)

            if file_type:
                if obj_size:
                    return u'%s, %s' % (file_type, obj_size)
                else:
                    return u'%s' % file_type

        elif item.portal_type in ['Link',]:
            url = self.getRemoteUrl(item)
            return self.getLinkType(url)

    def getItemHTMLInfo(self, item):

        if item.portal_type in ['Event',]:
            return self.render_j2(template='event_listing.j2', item=item)


class SubfolderView(FolderView):

    def include_item(self, _):

        if _._brain.is_folderish:
            return True

        if _.Type() in ('Collection',):
            return True

    # Only show folderish items
    def results(self):
        results = super(SubfolderView, self).results()
        return [x for x in results if self.include_item(x)]

class CollectionView(FolderView):

    batch_size = 99999

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def collection_behavior(self):
        return ICollection(aq_inner(self.context))

    @property
    def b_size(self):
        return getattr(self, '_b_size', self.collection_behavior.item_count)

    @property
    def b_start(self):
        b_start = getattr(self.request, 'b_start', None) or 0
        return int(b_start)

    def results(self, **kwargs):
        """Return a content listing based result set with results from the
        collection query.
        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument
        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        contentFilter = dict(self.request.get('contentFilter', {}))
        contentFilter.update(kwargs.get('contentFilter', {}))
        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.collection_behavior.results(**kwargs)
        return results

    def batch(self):
        # collection is already batched.
        return self.results()

class PhotoFolderView(FolderView):

    def image_size(self, _):

        if hasattr(_, 'image'):
            image = _.image
            return image.getImageSize()

        return (0,0)

    def image_class(self, _):

        (w,h) = self.image_size(_)

        if w and h:
            if w > h:
                return 'd-block w-100'

            return 'd-block h-100'

class DirectoryView(FolderView):

    batch_size = 99999

    def results(self):
        return self.context.people()

    def person_view(self, o):
        return o.restrictedTraverse('view')

    def show_short_bio(self):
        return not not getattr(self.context, 'show_short_bio', False)

    def jump_links(self, results):
        _ = OrderedDict([(x, None) for x in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")])

        for r in results:
            _letter = r.last_name[0].upper()

            if _letter in _ and not _[_letter]:
                _[_letter] = r.UID()

        return _

    def anchor(self, jump_links, r):
        _letter = r.last_name[0].upper()

        if _letter in jump_links and jump_links[_letter] == r.UID():
            return _letter

class EventView(_EventView, BaseView):

    data = None

    event_redirect_url = None

    index = ViewPageTemplateFile("templates/event_view.pt")

class EventRedirectView(EventView):

    @property
    def event_redirect_url(self):
        return getattr(self.context, 'event_url', None)

    def __call__(self):

        if self.anonymous and self.event_redirect_url:

            RESPONSE =  self.request.RESPONSE

            RESPONSE.setHeader(
                'Cache-Control',
                'max-age=0, s-maxage=3600, must-revalidate, public, proxy-revalidate'
            )

            return RESPONSE.redirect(self.event_redirect_url)

        return self.index()

class EventSummaryView(_EventSummaryView, BaseView):

    data = None

    @property
    def event_date(self):
        return self.get_event_date_range(self.context)

    @property
    def map_link(self):
        if IEvent.providedBy(self.context):
            return getattr(self.context, 'map_link', None)

class SocialMediaView(BaseView):
    pass

class ReindexObjectView(BaseView):

    def __call__(self):

        self.context.reindexObject()
        return self.request.response.redirect('%s?rescanned=1' % self.context.absolute_url())

class ExternalLinkCheckView(BaseView):

    def link_check(self):
        results = [x for x in ExternalLinkCheck(self.context).manual_check()]
        return results

class NewsItemView(BaseView):

    index = ViewPageTemplateFile("templates/news_item.pt")

    @property
    def article_link(self):
        return getattr(self.context, 'article_link', None)

    def item_date(self, item=None):
        return super(NewsItemView, self).item_date(self.context)

    def __call__(self):

        if self.anonymous and self.article_link:

            RESPONSE =  self.request.RESPONSE

            RESPONSE.setHeader(
                'Cache-Control',
                'max-age=0, s-maxage=3600, must-revalidate, public, proxy-revalidate'
            )

            return RESPONSE.redirect(self.article_link)

        return self.index()

class SiteMapView(_SiteMapView):

    exclude_types = [
        'Image',
        'Event',
    ]

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    @memoize
    def exclude_paths(self):

        queries = [
            {
                'exclude_from_robots' : True
            },
            {
                'review_state' : ['private',],
            },
            {
                'Type' : 'Event',
                'end' : {
                    'query' : DateTime(),
                    'range' : 'max',
                }
            }
        ]

        paths = []

        for q in queries:
            results = self.portal_catalog.searchResults(q)
            paths.extend([x.getURL() for x in results])

        paths = set(paths)

        duplicate_paths = []

        for p in paths:
            _p = '%s/' % p

            duplicate_paths.extend([
                x for x in paths if x.startswith(_p)
            ])

        _paths = paths - set(duplicate_paths)

        return _paths

    def excluded(self, url):

        exclude_paths = self.exclude_paths

        # Filter out excluded paths
        if url in exclude_paths:
            return True

        if any([url.startswith('%s/' % x) for x in exclude_paths]):
            return True

    def objects(self):
        """Returns the data to create the sitemap."""

        query = {}

        utils = getToolByName(self.context, 'plone_utils')

        query['portal_type'] = utils.getUserFriendlyTypes()

        registry = getUtility(IRegistry)

        typesUseViewActionInListings = frozenset(
            registry.get('plone.types_use_view_action_in_listings', []))

        is_plone_site_root = IPloneSiteRoot.providedBy(self.context)

        if not is_plone_site_root:
            query['path'] = '/'.join(self.context.getPhysicalPath())

        query['is_default_page'] = True

        default_page_modified = OOBTree()

        for item in self.portal_catalog.searchResults(query):
            key = item.getURL().rsplit('/', 1)[0]
            value = (item.modified.micros(), item.modified.ISO8601())
            default_page_modified[key] = value

        # The plone site root is not catalogued.
        if is_plone_site_root:
            loc = self.context.absolute_url()
            date = self.context.modified()
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            yield {
                'loc': loc,
                'lastmod': lastmod,
                # 'changefreq': 'always',
                #  hourly/daily/weekly/monthly/yearly/never
                # 'prioriy': 0.5, # 0.0 to 1.0
            }

        query['is_default_page'] = False

        for item in self.portal_catalog.searchResults(query):

            # Don't include excluded types
            if item.Type in self.exclude_types:
                continue

            loc = item.getURL()
            date = item.modified

            # Filter out excluded paths
            if self.excluded(loc):
                continue

            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            if item.portal_type in typesUseViewActionInListings:
                loc += '/view'
            yield {
                'loc': loc,
                'lastmod': lastmod,
                # 'changefreq': 'always',
                #  hourly/daily/weekly/monthly/yearly/never
                # 'prioriy': 0.5, # 0.0 to 1.0
            }

@implementer(IPublishTraverse)
class TagsView(CollectionView):

    def publishTraverse(self, request, name):

        if name:
            if '|' in name:
                self.url_tags = sorted(name.split('|'))
            else:
                self.url_tags = [name]
        else:
            self.url_tags = []

        self.original_url = request.getURL()
        self.original_context = self.context

        self.context = self.tag_root

        return self

    @property
    def tags(self):

        if hasattr(self, 'url_tags') and self.url_tags:
            _tags = dict(self.adapted.selected_tags)
            _ = [_tags.get(x, None) for x in self.url_tags]
            return [x for x in _ if x]

    @property
    def tag_root(self):
        return self.adapted.tag_root

    @property
    def adapted(self):
        return ITagsAdapter(self.context)

    def results(self):
        return Batch(self.adapted.get_items(self.tags), 99999, start=0)

class TileLinksView(BaseView):

    @property
    def mosaic_types(self):

        all_types = self.portal_catalog.uniqueValuesFor('portal_type')

        for portal_type in all_types:
            fti = getUtility(IDexterityFTI, name=portal_type)

            if 'plone.layoutaware' in fti.behaviors:
                yield portal_type

    @property
    def errors(self):
        mosaic_types = [x for x in self.mosaic_types]

        results = self.portal_catalog.searchResults({
            'path' : "/".join(self.context.getPhysicalPath()),
            'portal_type' : mosaic_types
        })

        for r in results:
            o = r.getObject()
            check = TileLinksCheck(o)
            for _ in check.check():
                yield _

class TileLinksDataView(TileLinksView):

    def __call__(self):

        data = []

        for _ in self.errors:
            data.append({
                'uid' : _.data.context.UID(),
                'type' : _.data.context.Type(),
                'url' : _.data.context.absolute_url(),
                'title' : _.data.context.Title(),
                'tile_id' : _.data.tile_id,
                'link_label' : _.data.label,
                'link_url' : _.data.url,
                'correct_link_url' : _.data.correct_url,
            })

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(data, indent=4)

class SearchView(_SearchView, BaseView):

    def munge_search_term(self, q):
        for char in BAD_CHARS:
            q = q.replace(char, ' ')
        r = map(quote, q.split())
        phrase = '"%s"' % " ".join(r)
        r = " AND ".join(r)
        r = quote_chars(r) + '*'
        return " OR ".join([phrase, r])

    def types_list(self):

        def sort_key(x):
            return self.portal_types.getTypeInfo(x).Title()

        def allowed_types(x):
            product = self.portal_types.getTypeInfo(x).product

            if product in ('PloneFormGen',):
                if self.portal_types.getTypeInfo(x).Title() not in ('FormFolder'):
                    return False

            return True

        _ = super(SearchView, self).types_list()

        _ = [x for x in _ if allowed_types(x)]

        return sorted(_, key=sort_key)

    def tags_list(self):
        return self.portal_catalog.uniqueValuesFor('Tags')

    @property
    def show_filters(self):
        return self.enhanced_public_tags or not self.anonymous

    @property
    def search_path_title(self):
        search_path = self.request.get('path', None)

        if search_path:

            site_path = '/'.join(self.site.getPhysicalPath())

            path = search_path[len(site_path)+1:]

            if path:

                try:
                    o = self.site.restrictedTraverse(path)
                except:
                    pass
                else:
                    return o.Title()

class HideChildrenView(BrowserView):

    @property
    def preview(self):
        return not not self.request.form.get('preview', None)

    @property
    def exclude(self):
        return not self.request.form.get('show', False)

    def __call__(self):

        alsoProvides(self.request, IDisableCSRFProtection)

        exclude = self.exclude
        preview = self.preview

        rv = []

        if hasattr(self.context, 'listFolderContents'):

            for o in self.context.listFolderContents():

                _ = getattr(o.aq_base, 'exclude_from_nav', False)

                if not _:
                    rv.append("Visible: %s" % o.absolute_url())
                else:
                    rv.append("Hidden: %s" % o.absolute_url())

                if exclude != _:
                    rv.append("Setting 'exclude from nav' to %r" % exclude)

                    if not preview:
                        setattr(o.aq_base, 'exclude_from_nav', exclude)
                        o.reindexObject()

                rv.append("-" * 20)
        else:
            return "Not folderish."

        return '\n'.join(rv)

class RobotsView(BaseView):

    @property
    def exclude_paths(self):
        site_url = self.site.absolute_url()
        v = SiteMapView(self.context, self.request)
        _ = [x[len(site_url):] for x in v.exclude_paths]
        return sorted(_)

    def __call__(self):

        portal_state = getMultiAdapter(
            (self.context, self.request), name='plone_portal_state')

        portal_url = portal_state.portal_url()

        return self.render_j2(
            template='robots.j2',
            data={
                'portal_url' : portal_url,
                'paths' : self.exclude_paths,
            },
        )

class LayoutPolicy(_LayoutPolicy, BaseView):

    def bodyClass(self, template, view):

        _ = super(LayoutPolicy, self).bodyClass(template, view)

        _ = _.split()

        navigation_viewlet = self.navigation_viewlet
        department_id = navigation_viewlet.department_id
        navigation_theme = navigation_viewlet.navigation_theme

        if department_id:
            _.append('header-department-level')
            _.append('department-%s' % department_id)
            _.append('footer-department-level')

        else:
            _.append('header-college-level')
            _.append('footer-college-level')

        if navigation_theme:
            _.append('navigation-%s' % navigation_theme)

        return " ".join(_)

# Provides a combined JS file for all theme files
class ThemeJSView(BaseView):

    # Config
    ASSETS_DIR = "++resource++agsci.common/assets"

    FILES = [
        'js/jquery-3.2.1.min.js',
        'bootstrap/js/bootstrap.bundle.min.js',
        'js/jquery.bootstrap-dropdown-hover.min.js',
        'js/scrollreveal.min.js',
        'featherlight/featherlight.min.js',
        'js/jquery.mixitup.min.js',
        'js/agsci.js',
    ]

    def __call__(self):

        # Grab contents of all listed files.
        data = []

        for _ in self.FILES:

            js_file  = "%s/%s" % (self.ASSETS_DIR, _)

            try:
                resource = self.site.restrictedTraverse(js_file)
            except:
                raise Exception("Can't find JS file %s" % js_file)
            else:
                try:
                    _data = resource.GET()
                except:
                    pass
                else:

                    if _data and isinstance(_data, (unicode, str)):
                        data.append(u"/* Include file: %s */" % _)
                        data.append(safe_unicode(_data))

        # Set headers for caching and content type
        self.request.response.setHeader('Content-Type', 'text/javascript')
        self.request.response.setHeader(
            'Cache-Control',
            'max-age=60, s-maxage=3600, must-revalidate, public, proxy-revalidate'
        )

        # Combine files and return
        _ = u"\n".join(data)
        return _.encode('utf-8')
