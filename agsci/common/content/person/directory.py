from Products.CMFCore.utils import getToolByName
from Products.membrane.interfaces import IGroup
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from dexterity.membrane.behavior.group import IMembraneGroup, MembraneGroup
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import Interface, implementer

from agsci.common import AgsciMessageFactory as _

# Person Listing

# Row Schemas
class IPersonOrderRowSchema(Interface):

    username = schema.Choice(
        title=_(u"Name"),
        vocabulary='agsci.common.tiles.people',
        required=False,
    )

    order = schema.Choice(
        title=_(u"Order"),
        values=range(1,100),
        required=False
    )

# Person Listing
class IPersonListing(model.Schema):

    form.widget(show_people=DataGridFieldFactory)

    show_people = schema.List(
        title=u"People",
        description=u"Configure the People to show, and the order in which to show them. If other criteria (classifications or groups) are selected, this is only used to order the display, not as a filter.",
        value_type=DictRow(title=u"Person", schema=IPersonOrderRowSchema),
        required=False
    )

    show_classifications = schema.List(
        title=_(u"Show Classifications"),
        required=False,
        value_type=schema.Choice(vocabulary="agsci.common.person.classifications"),
    )

    show_groups = schema.List(
        title=_(u"Show Groups"),
        required=False,
        value_type=schema.Choice(vocabulary="agsci.common.person.groups"),
    )

    show_short_bio = schema.Bool(
        title=_(u"Show Short Bio"),
        description=_(u"Only works on detail view, not table view."),
        required=False,
    )

    show_jump_links = schema.Bool(
        title=_(u"Show Jump Links"),
        description=_(u"Only works on table view, not detail view."),
        default=False,
        required=False,
    )

class IPersonPublicationListing(IPersonListing):

    form.omitted(
        'show_classifications', 'show_groups', 'show_short_bio', 'show_jump_links',
    )

    show_people = schema.List(
        title=u"People",
        description=u"Configure the People for whom to show publications.",
        value_type=DictRow(title=u"Person", schema=IPersonOrderRowSchema),
        required=False
    )

class PersonListing(Container):

    @property
    def query(self):
        return {
            'Type' : 'Person',
            'sort_on' : 'sortable_title',
        }

    @property
    def order(self):
        order = {}

        for _config in self.people_config:
            _username = _config.get('username', None)
            _order = _config.get('order', None)

            if _username and _order:

                if _username not in order:
                    order[_username] = _order

        return order

    def get_field(self, field):
        if field:
            _ = getattr(self, field, [])

            if _ and isinstance(_, (list, tuple)):
                return list(_)

        return []

    @property
    def people_config(self):
        return self.get_field('show_people')

    @property
    def people_ids(self):
        return [x.get('username', None) for x in self.people_config if x.get('username', None)]

    @property
    def classifications(self):
        return self.get_field('show_classifications')

    @property
    def groups(self):
        return self.get_field('show_groups')

    def sort(self, _):
        order = self.order

        if not order:
            return _

        def get_order(x):
            _id = x.getId()
            return order.get(_id, 99999)

        return sorted(_, key=get_order)

    def people(self):
        portal_catalog = getToolByName(self, 'portal_catalog')

        query = self.query

        people_ids = self.people_ids
        classifications = self.classifications
        groups = self.groups

        if classifications or groups:

            if classifications:
                query['DirectoryClassification'] = classifications

            if groups:
                query['DirectoryGroup'] = groups

        elif people_ids:

            query['getId'] = people_ids

        elif self.Type() not in ('Directory',):

            return []

        return self.sort(
            [x.getObject() for x in portal_catalog.searchResults(query)]
        )

class PersonPublicationListing(PersonListing):
    pass

# Directory
class IDirectory(model.Schema):

    show_classifications = schema.List(
        title=_(u"Show Classifications"),
        required=False,
        value_type=schema.Choice(vocabulary="agsci.common.person.classifications"),
    )

    show_jump_links = schema.Bool(
        title=_(u"Show Jump Links"),
        description=_(u"Only works on table view, not detail view."),
        default=True,
        required=False,
    )

class Directory(PersonListing):
    pass

# Directory Group (one to many)
class IDirectoryGroup(IDirectory, IGroup):
    pass

class DirectoryGroup(Directory):

    @property
    def groups(self):
        return [self.Title(),]

@implementer(IGroup)
@adapter(IMembraneGroup)
class DirectoryMembraneGroup(MembraneGroup):

    def getGroupMembers(self):
        return ()

# Classification (one to one, in theory)
class IClassification(IDirectoryGroup):
    form.omitted('show_classifications')

class Classification(Directory):

    @property
    def classifications(self):
        return [self.Title(),]
