from Acquisition import aq_inner, aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from RestrictedPython.Utilities import same_type as _same_type
from RestrictedPython.Utilities import test as _test
from StringIO import StringIO
from plone.app.textfield.value import RichTextValue
from plone.app.workflow.browser.sharing import SharingView, AUTH_GROUP
from plone.autoform.interfaces import IFormFieldProvider
from plone.memoize.instance import memoize
from urllib import quote_plus
from zope import schema
from zope.component import getUtility, getMultiAdapter, getAdapters
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements, Interface
from zope.interface.interfaces import IMethod
from collective.z3cform.datagridfield import DictRow
import urlparse

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

    def getItemLeadImage(self, item=None, size='large'):

        hasLeadImage = False

        if not item:
            item = self.context
            from agsci.common.indexer import hasLeadImage as _hasLeadImage
            hasLeadImage = _hasLeadImage(self.context)()

        # Is a brain
        if hasattr(item, 'getURL'):
            url = item.getURL()
            hasLeadImage = item.hasLeadImage

        elif hasattr(item, 'absolute_url'):
            url = item.absolute_url()

        else:
            url = self.context.absolute_url()

        if size:
            return '%s/@@images/image/%s' % (url, size)

        return '%s/@@images/image' % (url,)

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
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    @property
    def context_state(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def anonymous(self):
        return self.portal_state.anonymous()

    # Providing Restricted Python "test" method
    def test(self, *args):
        return _test(*args)

    # Providing Restricted Python "test" same_type
    def same_type(self, arg1, *args):
        return _same_type(arg1, *args)

    @property
    def hasTiledContents(self):
        if hasattr(self.context, 'getLayout') and self.context.getLayout() in ['folder_summary_view', 'subfolder_view']:
            return ITileFolder.providedBy(self.context)
        return False


    @property
    def use_view_action(self):
        return getToolByName(self.context, 'portal_properties').get("site_properties").getProperty('typesUseViewActionInListings', ())

    def isPublication(self, item):

        publication_interfaces = [
            'agsci.UniversalExtender.interfaces.IUniversalPublicationExtender',
            'agsci.UniversalExtender.interfaces.IFilePublicationExtender',
            'agsci.ExtensionExtender.interfaces.IExtensionPublicationExtender',
        ]

        object_provides = getattr(item, 'object_provides', [])

        if object_provides:
            return (len(set(object_provides) & set(publication_interfaces)) > 0)

        return False

    def getItemURL(self, item):

        item_type = item.portal_type

        if hasattr(item, 'getURL'):
            item_url = item.getURL()
        else:
            item_url = item.absolute_url()

        # Logged out
        if self.anonymous:
            if item_type in ['Image',] or \
               (item_type in ['File',] and \
                    (self.isPublication(item) or not self.getFileType(item))):
                return item_url + '/view'
            else:
                return item_url
        # Logged in
        else:
            if item_type in self.use_view_action:
                return item_url + '/view'
            else:
                return item_url

    def getIcon(self, item):

        if hasattr(item, 'getIcon'):
            if hasattr(item.getIcon, '__call__'):
                return item.getIcon()
            else:
                return item.getIcon

        return None

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

    def getFileType(self, item):

        icon = self.getIcon(item)

        if icon:
            icon = icon.split('.')[0]

        return self.fileExtensionIcons().get(icon, None)

    def getLinkType(self, url):

        if '.' in url:
            icon = url.strip().lower().split('.')[-1]
            return self.fileExtensionIcons().get(icon, None)

        return None

    def getItemSize(self, item):
        if hasattr(item, 'getObjSize'):
            if hasattr(item.getObjSize, '__call__'):
                return item.getObjSize()
            else:
                return item.getObjSize
        return None

    def getRemoteUrl(self, item):
        if hasattr(item, 'getRemoteUrl'):
            if hasattr(item.getRemoteUrl, '__call__'):
                return item.getRemoteUrl()
            else:
                return item.getRemoteUrl
        return None

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

        return None

    def getItemClass(self, item, layout='folder_listing'):

        # Default classes for all views
        item_class = ['tileItem', 'visualIEFloatFix']

        return " ".join(item_class)

    @property
    def getTileColumns(self):
        return getattr(self.context, 'tile_folder_columns', '3')

    @memoize
    def getSection(self):
        v = self.context.restrictedTraverse('@@agcommon_utilities')
        return v.getSection()

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def portal_url(self):
        return self.portal.absolute_url()

    def showPersonAreas(self):
        return getattr(self.context, 'show_person_areas', True)

    @property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')

    def getCurrentUser(self):
        return self.portal_membership.getAuthenticatedMember()

    def isDefaultPage(self):
        if not hasattr(self.context.aq_parent, 'getDefaultPage'):
            return False

        return (self.context.getId() == self.context.aq_parent.getDefaultPage())

class DegreeListingView(BaseView):

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

    @property
    def image(self):
        return self.getItemLeadImage(size=None)

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

    @property
    def card_image_class(self):

        if self.card_format in ('vertical',):
            return 'col-12 px-0 mb-2'

        return 'col-12 col-md-5 col-sm-12 px-0'

    @property
    def card_details_class(self):
        if self.card_format in ('vertical',):
            return 'col-12 px-0'

        return 'col-12 col-sm-12 col-md-7 mt-2 mt-md-0 pl-0 px-sm-0 pr-0 pl-md-3 pl-sm-0'

class PersonCardVerticalView(PersonCardView):

    card_format = 'vertical'

class DirectoryView(BaseView):

    @property
    def people(self):
        return self.context.people()

    def person_view(self, o):
        return o.restrictedTraverse('view')

class SocialMediaView(BaseView):
    pass