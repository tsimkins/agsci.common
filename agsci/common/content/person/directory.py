from Products.CMFCore.utils import getToolByName
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema

from agsci.common import AgsciMessageFactory as _

# Directory

class IDirectory(model.Schema):

    pass

class Directory(Container):

    def listPeople(self, modified=None):
        portal_catalog = getToolByName(self, 'portal_catalog')

        query = {'Type' : 'Person', 'sort_on' : 'sortable_title'}

        if modified:
            query['modified'] = modified

        return map(lambda x: x.getObject(), portal_catalog.searchResults(query))