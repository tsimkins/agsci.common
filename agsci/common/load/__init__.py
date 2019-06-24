from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from bs4 import BeautifulSoup
from plone.app.linkintegrity.handlers import modifiedContent
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable, IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEventAccessor
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from plone.uuid.interfaces import ATTRIBUTE_NAME
from urlparse import urljoin, urlparse
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.component.interfaces import ComponentLookupError
from zope.schema import getFieldsInOrder

import base64
import json
import re
import requests
import urllib2

from ..utilities import scrub_html

# Regular expression to validate UID
uid_re = re.compile("^[0-9abcedf]{32}$", re.I|re.M)

# Class to hold json data and return as attributes
class json_data_object(object):

    def __init__(self, data={}):
        self.data = data

    def __getattribute__(self, name):

        # Don't proxy the 'data' attribute
        if name == 'data':
            return object.__getattribute__(self, name)

        # Otherwise, return the value of the key in the data dict
        if self.data.has_key(name):
            value = self.data.get(name, '')

            if value:
                if isinstance(value, dict) and value.has_key('value'):
                    return value['value']
                return value

        else:
            # Get based on original ID rather than JSON key
            for (k,v) in self.data.iteritems():
                if isinstance(v, dict):
                    _id = v.get('info', {}).get('id', None)
                    if _id == name:
                        return self.__getattribute__(k)

        # Then get the attribute on the object itself, or return blank on error
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return ''

class ContentImporter(object):

    manual_types_mapping = {
        'Home Page' : 'agsci_homepage',
        'Photo Folder' : 'agsci_photofolder',
        'Form Folder' : 'Folder',
    }

    fields_mapping = {
        'show_leadimage_context' : 'image_show',
    }

    valid_layouts = [
        'subfolder_view',
    ]

    @property
    def types_mapping(self):
        _ = dict([(x.Title(), x.getId()) for x in self.portal_types.listTypeInfo()])
        _.update(self.manual_types_mapping)
        return _

    exclude_fields = [
        'title',
        'id',
        'description',
        'image',
        'file',
        'effective_date',
        'expiration_date',
        'text',
        'language',
    ]

    default_type = 'Folder'

    def __init__(self, path, UID, api_url, context=None, **kwargs):
        if path.startswith('/'):
            path = path[1:]

        if path.endswith('/'):
            path = self.path[:-1]

        self.path = path
        self.UID = UID
        self.api_url = api_url

        self.import_path = context

        try:
            self.data = json_data_object(self.json_data)
        except:
            self.data = json_data_object({})

        if isinstance(self.path, unicode):
            self.path = self.path.encode('utf-8')

    @property
    def json_data(self):
        parsed_url = urlparse(self.api_url)

        # Local file
        if not parsed_url.scheme:
            return json.loads(open(parsed_url.path, "r").read())

        # Remote URL
        return requests.get(self.api_url).json()

    @property
    def portal_types(self):
        return getToolByName(self.site, 'portal_types')

    @property
    def wftool(self):
        return getToolByName(self.site, "portal_workflow")

    @property
    def site(self):
        if self.import_path:
            return self.import_path

        return getSite()

    @property
    def context(self):
        try:
            _id = self.getId()

            if _id in self.parent.objectIds():
                return self.parent[_id]

            _ = dict([(x.UID(), x) for x in self.parent.listFolderContents()])

            return _.get(self.UID, None)

        except:
            pass

    @property
    def parent(self):
        parent_path = "/".join(self.path.split('/')[:-1])

        if parent_path:

            # Return the parent path object if it exists.  If not, return the
            # 'imports' directory at the root of the site if it exists.
            # Finally, just raise an error.
            # This is to prevent random content from coming in at the site root.
            try:
                return self.site.restrictedTraverse(parent_path)
            except:

                if 'imports' in self.site.objectIds():
                    return self.site['imports']

                raise Exception('No Parent found')

        return self.site

    @property
    def exists(self):
        return not not self.context

    @property
    def portal_type(self):

        fti = self.product_fti

        if fti:
            return fti.getId()

        return self.default_type

    @property
    def product_fti(self):

        _type = self.data.type
        _type = self.types_mapping.get(_type, _type)

        try:
            return getUtility(IDexterityFTI, _type)
        except ComponentLookupError:
            return None

    @property
    def schema(self):
        fti = self.product_fti

        if fti:
            return fti.lookupSchema()

    @property
    def behaviors(self):
        fti = self.product_fti

        if fti:
            for _ in fti.behaviors:
                try:
                    __ = getUtility(IBehavior, _)

                    if __:
                        yield __.interface

                except ComponentLookupError:
                    pass

    @property
    def fields(self):

        rv = []

        schemata = [self.schema, ]
        schemata.extend(self.behaviors)

        for _ in schemata:
            rv.extend(getFieldsInOrder(_))

        return [x[0] for x in rv]

    def fix_html(self, html):
        updated = False

        html = scrub_html(html)

        soup = BeautifulSoup(html, 'lxml')

        # Zap class on table so Diazo replacement will work.
        for table in soup.findAll('table'):
            updated = True
            if hasattr(table, 'class'):
                del table['class']

        for img in soup.findAll('img'):
            src = img.get('src', None)
            if src:
                img_src = self.get_img_url(src)
                if img_src:
                    updated = True
                    img['src'] = img_src

        for a in soup.findAll('a'):
            href = a.get('href', None)
            if href:
                uid = self.get_resource_uid(href)
                if uid:
                    updated = True
                    a['href'] = 'resolveuid/%s' % uid

        # Fix heading levels to an h2 if all headings are the same level
        headings = soup.findAll(['h%x' % x for x in range(1,7)])
        heading_names = list(set([x.name for x in headings]))

        if len(heading_names) == 1:

            hx = heading_names[0]

            for _h in soup.findAll(hx):
                if _h.name != 'h2':
                    _h.name = 'h2'
                    updated = True

        if updated:
            soup.body.hidden = True
            return unicode(soup.body)

        return html


    @property
    def html(self):
        for _ in [
            self.data.text,
            self.data.folder_text,
        ]:

            if _:
                return self.fix_html(_)

        return ''

    def get_img_url(self, src):
        if src:
            src = safe_unicode(src).encode('utf-8')
            if src.startswith('/'):
                src = src[1:]
            if '@@' in src:
                _src = src[:src.index('@@')-1]
                _view = src[src.index('@@'):]
                try:
                    _img = self.context.restrictedTraverse(_src)
                except:
                    pass
                else:
                    uid = _img.UID()
                    new_src = 'resolveuid/%s' % uid
                    images_view = _img.restrictedTraverse('@@images')
                    (field, scale) = _view.split('/')[-2:]
                    if not images_view.scale(field, scale):
                        scale = 'gallery'
                    _view = '@@images/%s/%s' % (field, scale)
                    return '%s/%s' % (new_src, _view)
            else:
                _ = self.get_resource_uid(src)

                if _:
                    return 'resolveuid/%s' % _

    def get_resource_uid(self, path):
        path = safe_unicode(path).encode('utf-8')

        if path.startswith('/'):
            path = path[1:]

        segments = path.split('/')

        if segments[-1].startswith('image_') or segments[-1] in ('view',):
            undef = segments.pop()
            path = "/".join(segments)

        if path.startswith('..'):

            context = self.context

            if context:
                base_url = context.absolute_url()
            else:
                base_url = '%s/%s' % (self.parent.absolute_url(), self.getId())

            path = urljoin(base_url, path)[len(getSite().absolute_url())+1:]

        for site in (self.site, getSite()):

            try:
                _ = site.restrictedTraverse(path)
            except:
                continue
            else:
                return _.UID()

    def data_to_image_field(self, data, contentType='', filename=None):

        if filename:
            filename = filename.decode('utf-8')
        else:
            filename = u'image'

        return NamedBlobImage(
            filename=filename,
            data=base64.b64decode(data)
        )

    def data_to_file_field(self, data, contentType='', filename=None):

        if filename:
            filename = filename.decode('utf-8')

        return NamedBlobFile(
            filename=filename,
            contentType=contentType,
            data=base64.b64decode(data)
        )

    @property
    def image(self):
        for _ in [
            self.data.lead_image,
            self.data.image,
        ]:
            if _:
                return self.data_to_image_field(
                    data=_['data'],
                    contentType=_['content_type'],
                    filename=_.get('filename', 'image'),
                )

    @property
    def file(self):
        for _ in [
            self.data.file,
        ]:
            if _:
                return self.data_to_file_field(
                    data=_['data'],
                    contentType=_['content_type'],
                    filename=_.get('filename', 'file'),
                )

    @property
    def review_state(self):
        if self.exists:
            try:
                return self.wftool.getInfoFor(self.context, 'review_state')
            except WorkflowException:
                pass

    def getId(self):
        return safe_unicode(self.data.id).encode('utf-8')

    def __call__(self):

        if not self.data.data:
            raise Exception("No data provided.")

        parent = self.parent

        if not parent:
            raise Exception("Cannot find parent object for %s" % self.path)

        _id = self.getId()

        if not self.exists:

            item = createContentInContainer(
                parent,
                self.portal_type,
                id=_id,
                title=self.data.title,
                description=self.data.description,
                checkConstraints=False
            )

            # Set UID
            setattr(item, ATTRIBUTE_NAME, self.UID)

        else:

            # If the item exists, and it's published, no further changes
            if self.review_state in ['published',]:
                return

            item = self.context

        # Set subject (tags)
        if self.data.subject:
            item.setSubject(list(self.data.subject))

        # Set HTML
        html = self.html

        if html:

            item.text = RichTextValue(
                raw=html,
                mimeType=u'text/html',
                outputMimeType='text/x-html-safe'
            )

        # Set File field
        file = self.file

        if file:
            item.file = self.file

        # Set Lead Image or Image field
        image = self.image

        if image:
            item.image = image

            # Unset full width field if image is too small, or is portrait.
            try:
                (w,h) = image.getImageSize()
            except:
                pass
            else:
                if w < h or w < 600:
                    item.image_full_width = False

        # Set field values
        for field in self.fields:

            set_field = self.fields_mapping.get(field, field)

            if set_field not in self.exclude_fields:
                value = getattr(self.data, field, None)

                if value or isinstance(value, (bool,)):
                    setattr(item, set_field, value)

        # Set collection criteria
        if self.portal_type in ('Collection', 'Newsletter'):
            if self.data.collection_criteria:
                item.setQuery(self.data.collection_criteria)

            if self.data.collection_sort_field:
                item.setSort_on(self.data.collection_sort_field)

                if self.data.collection_sort_reversed:
                    item.setSort_reversed(True)

        # Set default page
        if self.data.default_page:
            default_page_id = safe_unicode(self.data.default_page).encode('utf-8')
            self.context.setDefaultPage(default_page_id)
        else:

            # Set layout if no default page
            layout = self.data.layout

            if layout in self.valid_layouts:
                item.setLayout(layout)

        # Set dates
        effective = self.data.effective_date
        expires = self.data.expiration_date

        if effective:
            item.setEffectiveDate(DateTime(effective))

        if expires:
            item.setExpirationDate(DateTime(expires))

        # Set references
        modifiedContent(item, None)

        # Reindex
        item.reindexObject()