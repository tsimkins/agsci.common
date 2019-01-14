from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEventAccessor
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from plone.uuid.interfaces import ATTRIBUTE_NAME
from zope.component.hooks import getSite

from urlparse import urljoin

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

        # Then get the attribute on the object itself, or return blank on error
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return ''

class ContentImporter(object):

    types_mapping = {}

    default_type = 'Folder'

    def __init__(self, path, UID, getId, api_url, **kwargs):
        self.path = path
        self.UID = UID
        self.getId = getId
        self.api_url = api_url
        self.data = json_data_object(self.json_data)
        
        if isinstance(self.path, unicode):
            self.path = self.path.encode('utf-8')

    @property
    def json_data(self):
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

        try:
            return self.site.restrictedTraverse(parent_path)
        except:
            pass

    @property
    def exists(self):
        return not not self.context

    @property
    def product_type(self):

        _type = self.data.type
        
        if self.types_mapping.has_key(_type):
            return self.types_mapping[_type]

        for fti in self.portal_types.listTypeInfo():
            if fti.Title() == _type:
                return fti.getId()
        
        return self.default_type

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
            id=self.data.id,
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