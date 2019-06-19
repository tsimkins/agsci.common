from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from collective.z3cform.datagridfield import DictRow
from plone import api
from plone.app.dexterity.browser.folder_listing import FolderView as _FolderView
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.component import getUtility

from agsci.common.content.check import ExternalLinkCheck
from agsci.common.content.degrees import IDegree
from agsci.common.indexer import degree_index_field
from agsci.common.utilities import get_fields_by_type, toLocalizedTime
from agsci.common import object_factory
from agsci.common.interfaces import ILocationAdapter

try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite

class BaseView(BrowserView):

    image_size = 'large'

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
                    value = [object_factory(**x) for x in value]

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
        if item.effective:
            return toLocalizedTime(item.effective)

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

        if item_type in self.use_view_action:
            return item_url + '/view'
        else:
            return item_url

    @property
    def use_view_action(self):

        if not self.anonymous:
            registry = getUtility(IRegistry)
            return registry.get('plone.types_use_view_action_in_listings', [])

        return []

class DegreeListingView(BaseView):

    image_size = None

    def getQuery(self):
        return {'Type' : 'Degree', 'sort_on' : 'sortable_title'}

    def getFolderContents(self):
        return self.portal_catalog.queryCatalog(self.getQuery())


class DegreeView(BaseView):

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

class PersonCardView(PersonView):

    card_format = 'horizontal'
    border = True

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

class PersonCardVerticalNoBorderView(PersonCardVerticalView):
    border = False

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

class SubfolderView(FolderView):

    # Only show folderish items
    def results(self):
        results = super(SubfolderView, self).results()
        return [x for x in results if x._brain.is_folderish]

class CollectionView(FolderView):

    def batch(self):
        return self.context.queryCatalog()

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

    @property
    def results(self):
        return self.context.people()

    def person_view(self, o):
        return o.restrictedTraverse('view')

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
