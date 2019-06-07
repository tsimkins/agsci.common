from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from collective.z3cform.datagridfield import DictRow
from plone import api
from plone.app.dexterity.browser.folder_listing import FolderView as _FolderView
from zope import schema

from agsci.common.content.degrees import IDegree
from agsci.common.indexer import degree_index_field
from agsci.common.utilities import get_fields_by_type
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

    @property
    def show_date(self):
        return getattr(aq_base(self.context), 'show_date', False)

    @property
    def show_image(self):
        return getattr(aq_base(self.context), 'show_image', False)

    @property
    def show_read_more(self):
        return getattr(aq_base(self.context), 'show_read_more', False)

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def anonymous(self):
        return api.user.is_anonymous()

    @property
    def use_view_action(self):
        return getToolByName(self.context, 'portal_properties').get("site_properties").getProperty('typesUseViewActionInListings', ())

    def getItemURL(self, item):

        item_type = item.portal_type

        if hasattr(item, 'getURL'):
            item_url = item.getURL()
        else:
            item_url = item.absolute_url()

        # Logged out
        if self.anonymous:
            if item_type in ['Image', 'File']:
                return item_url + '/view'
            else:
                return item_url
        # Logged in
        else:
            if item_type in self.use_view_action:
                return item_url + '/view'
            else:
                return item_url

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
            from agsci.common.indexer import hasLeadImage as _hasLeadImage
            has_image = _hasLeadImage(self.context)()

        # Is a brain
        elif hasattr(item, 'hasLeadImage'):
            has_image = item.hasLeadImage

        return has_image

    def show_item_image(self, item):
        return self.show_image and  self.item_has_image(item)

    def item_class(self, item):
        _ = ['col-12', 'order-2', 'order-md-1', 'mt-0', 'px-0']

        if self.show_item_image(item):
            _.extend(['col-md-8', 'col-lg-7'])

        return " ".join(_)

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
    pass

class CollectionView(FolderView):

    def batch(self):
        return self.context.queryCatalog()

class DirectoryView(FolderView):

    @property
    def results(self):
        return self.context.people()

    def person_view(self, o):
        return o.restrictedTraverse('view')

class SocialMediaView(BaseView):
    pass