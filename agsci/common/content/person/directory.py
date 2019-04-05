from Products.CMFCore.utils import getToolByName
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema

from agsci.common import AgsciMessageFactory as _

# Directory

class IDirectory(model.Schema):
    pass

class IClassification(IDirectory):
    pass

class Directory(Container):

    @property
    def query(self):
        return {'Type' : 'Person', 'sort_on' : 'sortable_title'}

    def people(self, modified=None):
        portal_catalog = getToolByName(self, 'portal_catalog')

        query = self.query

        if modified:
            query['modified'] = modified

        return map(lambda x: x.getObject(), portal_catalog.searchResults(query))

class Classification(Directory):

    @property
    def query(self):
        _ = super(Classification, self).query
        _['DirectoryClassification'] = self.Title()
        return _