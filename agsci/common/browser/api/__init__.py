from Acquisition import ImplicitAcquisitionWrapper
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import BrowserView
from bs4 import BeautifulSoup
from datetime import datetime
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage, NamedBlobFile
from z3c.relationfield.relation import RelationValue
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface.interface import Method

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import base64
import json
import re

from agsci.common.content.check import ExternalLinkCheck
from agsci.common.utilities import get_fields_by_type, toISO

from json import JSONEncoder

class CustomEncoder(JSONEncoder):

    @property
    def request(self):
        return getRequest()

    @property
    def site(self):
        return getSite()

    @property
    def bin(self):
        return self.request.form.get('bin', '').lower() not in ('0', 'false')

    def html_to_text(self, html):
        portal_transforms = getToolByName(self.site, 'portal_transforms')
        text = portal_transforms.convert('html_to_text', html).getData()
        return text

    def default(self, o):

        # If blob field type, encode binary data and
        # include mime type
        if isinstance(o, (NamedBlobImage, NamedBlobFile)):

            # Skip if we're not providing binary info
            if self.bin:

                blob_data = o.data

                if isinstance(blob_data, ImplicitAcquisitionWrapper):
                    blob_data = blob_data.data

                if blob_data:

                    return {
                        'content_type' : o.contentType,
                        'data' : base64.b64encode(blob_data),
                        'filename' : o.filename,
                    }

            return None

        elif isinstance(o, (datetime, DateTime)):
            return toISO(o)

        elif isinstance(o, (RelationValue,)):
            return o.to_object.UID()

        elif isinstance(o, (RichTextValue,)):

            html = o.raw

            if html:
                soup = BeautifulSoup(html, features="lxml")
                soup.html.hidden = True
                soup.body.hidden = True

                # Convert relative img src to full URL path
                for img in soup.findAll('img'):
                    src = img.get('src')
                    if src and not src.startswith('http'):
                        #img['src'] = urljoin(self.context.absolute_url(), src)
                        pass

                return {
                    'html' : repr(soup),
                    'text' : self.html_to_text(html).strip(),
                    'output' : o.output
                }

        return json.JSONEncoder.default(self, o)

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

# Regular expression to validate UID
uid_re = re.compile("^[0-9abcedf]{32}$", re.I|re.M)

class JSONDumpView(BrowserView):

    recursive = True

    exclude_fields = [
        'publications',
    ]

    # http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
    def format_key(self, name):
        s1 = first_cap_re.sub(r'\1_\2', name)
        return all_cap_re.sub(r'\1_\2', s1).lower()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def __call__(self):
        json = self.getJSON()
        self.request.response.setHeader('Content-Type', 'application/json')
        return json

    @property
    def base_context(self):
        return self.context.aq_base

    @property
    def fields(self):
        return get_fields_by_type(self.context.portal_type)

    def field_info(self, field):

        return {
            'id' : self.format_key(field.getName()),
            'label' : self.translate(field.title),
            'type' : field.__class__.__name__,
        }

    @property
    def data(self):

        fields = self.fields

        data = {
            'url' : {
                'info' : {},
                'value' : self.context.absolute_url(),
            },
            'uid' : {
                'info' : {},
                'value' : self.context.UID(),
            },
            'relative_path' : {
                'info' : {},
                'value' : self.relative_path,
            },
            'review_state' : {
                'info' : {},
                'value' : self.review_state,
            },
            'type' : {
                'info' : {},
                'value' : self.context.Type(),
            },
            'default_page' : {
                'info' : {},
                'value' : self.default_page,
            },
            'layout' : {
                'info' : {},
                'value' : self.layout,
            },
        }

        # Because something weird happens with subjects field.
        if 'subjects' in fields:
            fields['subject'] = fields['subjects']

        for (_name, _field) in fields.items():

            # Don't provide explicitly excluded fields
            if _name in self.exclude_fields:
                continue

            if isinstance(_field, Method):
                continue

            v = getattr(self.base_context, _name, None)

            if hasattr(v, '__call__'):
                v = v()

            if v is None:
                continue

            field_name = self.format_key(_name)
            value = v

            data[field_name] = {
                'info' : self.field_info(_field),
                'value' : value,
            }

        return data

    @property
    def review_state(self):
        try:
            return self.portal_workflow.getInfoFor(self.context, 'review_state')
        except:
            return None

    @property
    def site(self):
        return getSite()

    @property
    def site_path(self):
        return "/".join(self.site.getPhysicalPath())

    @property
    def context_path(self):
        return "/".join(self.context.getPhysicalPath())

    @property
    def relative_path(self):
        return self.getRelativePath("/".join(self.context.getPhysicalPath()))

    def getRelativePath(self, path):
        site_path_length = len(self.site_path)
        return path[site_path_length+1:]

    def getJSON(self):
        return json.dumps(self.data, indent=4, sort_keys=True, cls=CustomEncoder)

    @property
    def portal_workflow(self):
        return getToolByName(self.context, "portal_workflow")

    @property
    def translation_service(self):
        return getToolByName(self.context, 'translation_service')

    def translate(self, v):
        return self.translation_service.translate(v, target_language="en")

    @property
    def default_page(self):
        if hasattr(self.context, 'getDefaultPage'):
            _ =  self.context.getDefaultPage()
            if _ in self.context.objectIds():
                return _

    @property
    def layout(self):
        if not self.default_page:
            if hasattr(self.context, 'getLayout'):
                return self.context.getLayout()

class ContainerJSONDumpView(JSONDumpView):

    @property
    def contents(self):

        _ = []

        now = DateTime()

        for o in self.context.listFolderContents():
            if o.expires() > now:
                v = o.restrictedTraverse('@@dump-json')
                v.recursive = False
                _.append(v.data)

        return _

    @property
    def data(self):
        data = super(ContainerJSONDumpView, self).data

        if self.recursive:
            data['contents'] = self.contents

        return data

class PloneSiteJSONDumpView(JSONDumpView):

    excluded_types = [
        u'Faculty/Staff Directory',
        u'Relations Library',
    ]

    json_api_view = "@@dump-json"

    @property
    def data(self):

        # Return value
        data = []

        # Get all child objects
        results = self.portal_catalog.searchResults({
            'path' : {
                'query' : self.context_path,
                'depth' : 1,
            }
        })

        # Remove objects of types that are excluded
        results = [x for x in results if x.Type not in self.excluded_types]

        # Get the path of the remaining objects
        paths = [x.getPath() for x in results]

        # If the object on which the view is called is not a Plone site, include
        # it as well.
        if not IPloneSiteRoot.providedBy(self.context):
            paths.append(self.context_path)

        # Find everything inside these paths
        results = self.portal_catalog.searchResults({
            'path' : paths
        })

        # Create data structure of content
        for r in results:

            data.append({
                'path' : self.getRelativePath(r.getPath()),
                'getId' : r.getId,
                'UID' : r.UID,
                'Type' : r.Type,
                'api_url' : '%s/%s' % (r.getURL(), self.json_api_view),
            })

        # Sort by the length of the path
        data.sort(key=lambda x: (len(x['path']), x['getId']))

        return data

class ExternalLinksView(JSONDumpView):

    @property
    def data(self):

        # Return value
        data = []

        results = self.portal_catalog.searchResults({
            'ContentErrorCodes' : 'ExternalLinkCheck',
        })

        for r in results:

            o = r.getObject()

            c = ExternalLinkCheck(o)

            links = [x for x in c.getExternalLinks()]

            if links:
                data.append({
                    'uid' : r.UID,
                    'url' : r.getURL(),
                    'title' : r.Title,
                    'type' : r.Type,
                    'links' : [dict(zip(['href', 'label'], x)) for x in links],
                    'review_state' : r.review_state,
                })

        return data
