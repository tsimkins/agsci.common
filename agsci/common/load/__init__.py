from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
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

    types_mapping = {}

    exclude_fields = [
        'title',
        'id',
        'description',
        'image',
        'file',
    ]

    default_type = 'Folder'

    def __init__(self, path, UID, api_url, **kwargs):
        if path.startswith('/'):
            path = path[1:]

        if path.endswith('/'):
            path = self.path[:-1]

        self.path = path
        self.UID = UID
        self.api_url = api_url
        self.data = json_data_object(self.json_data)

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
    def site(self):
        return getSite()

    @property
    def context(self):
        try:
            return self.site.restrictedTraverse(self.path)
        except:
            pass

    @property
    def parent(self):
        parent_path = "/".join(self.path.split('/')[:-1])

        if parent_path:

            try:
                return self.site.restrictedTraverse(parent_path)
            except:
                pass

        return self.site

    @property
    def exists(self):
        return not not self.context

    @property
    def product_type(self):

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

    @property
    def html(self):
        for _ in [
            self.data.text,
            self.data.folder_text,
        ]:
            if _:
                return _
        return ''

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
                )


    def __call__(self):
        if self.exists:
            raise Exception("%s already exists." % self.path)

        parent = self.parent

        if not parent:
            raise Exception("Cannot find parent object for %s" % self.path)

        item = createContentInContainer(
            parent,
            self.product_type,
            id=safe_unicode(self.data.id).encode('utf-8'),
            title=self.data.title,
            description=self.data.description,
            checkConstraints=False
        )

        # Set UID
        setattr(item, ATTRIBUTE_NAME, self.UID)

        # Set HTML
        html = self.html

        if html:

            item.text = RichTextValue(
                raw=html,
                mimeType=u'text/html',
                outputMimeType='text/x-html-safe'
            )

        # Set Lead Image
        image = self.image

        if image:
            item.image = image

        for field in self.fields:
            if field not in self.exclude_fields:
                value = getattr(self.data, field, None)

                if value:
                    setattr(item, field, value)
