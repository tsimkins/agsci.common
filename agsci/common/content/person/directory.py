from Products.CMFCore.utils import getToolByName
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema

from agsci.common import AgsciMessageFactory as _

# Directory

class IDirectory(model.Schema):

    show_classifications = schema.List(
        title=_(u"Show Classifications"),
        required=True,
        value_type=schema.Choice(vocabulary="agsci.common.person.classifications"),
    )

class IClassification(IDirectory):
    pass

class IDirectoryGroup(IClassification):
    pass

class Directory(Container):

    @property
    def query(self):
        return {
            'Type' : 'Person',
            'sort_on' : 'sortable_title',
        }

    def people(self, modified=None):
        portal_catalog = getToolByName(self, 'portal_catalog')

        query = self.query

        if modified:
            query['modified'] = modified

        show_classifications = getattr(self, 'show_classifications', [])

        if show_classifications and isinstance(show_classifications, (list, tuple)):
            query['DirectoryClassification'] = show_classifications

        return map(lambda x: x.getObject(), portal_catalog.searchResults(query))

class Classification(Directory):

    @property
    def query(self):
        _ = super(Classification, self).query
        _['DirectoryClassification'] = self.Title()
        return _

class DirectoryGroup(Classification):

    @property
    def query(self):
        _ = super(Classification, self).query
        _['DirectoryGroup'] = self.Title()
        return _