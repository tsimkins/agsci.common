from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements

from agsci.common.interfaces import ITagsAdapter
from agsci.common.utilities import getNavigationViewlet

class BaseVocabulary(object):

    implements(IVocabularyFactory)

    @property
    def site(self):
        return getSite()

    @property
    def portal_catalog(self):
        return getToolByName(self.site, 'portal_catalog')

    @property
    def navigation_viewlet(self):
        return getNavigationViewlet()

    @property
    def department_id(self):
        return self.navigation_viewlet.department_id

class StaticVocabulary(BaseVocabulary):

    preserve_order = False

    items = ['N/A',]

    def __call__(self, context):

        unsorted_items = self.items

        items = list(set(unsorted_items))

        def sort_key(x):
            return unsorted_items.index(x)

        if self.preserve_order:
            items.sort(key=sort_key)
        else:
            items.sort()

        terms = [SimpleTerm(x, title=x) for x in items]

        return SimpleVocabulary(terms)

class KeyValueVocabulary(BaseVocabulary):

    items = [
        ('N/A', 'N/A'),
    ]

    def __call__(self, context):

        return SimpleVocabulary(
            [
                SimpleTerm(x, title=y) for (x, y) in self.items
            ]
        )


# Public Tags
class PublicTagsVocabulary(BaseVocabulary):

    def items(self, context):
        return ITagsAdapter(context).available_tags

    def __call__(self, context):

        items = self.items(context)

        return SimpleVocabulary(
            [
                SimpleTerm(x, title=x) for x in items
            ]
        )

        return []

class AllPublicTagsVocabulary(BaseVocabulary):

    @property
    def items(self):
        return self.portal_catalog.uniqueValuesFor('Tags')

    def __call__(self, context):

        items = self.items

        return SimpleVocabulary(
            [
                SimpleTerm(x, title=x) for x in items
            ]
        )

        return []

# Directory classifications for people
class PersonClassificationsVocabulary(StaticVocabulary):

    preserve_order = True

    defaults = [
        "Adjunct Faculty",
        "Affiliate Faculty",
        "Emeritus Faculty",
        "Faculty",
        "Graduate Students",
        "Instructors",
        "Post-Doctoral Scholars",
        "Researchers",
        "Staff",
        "Undergraduate Students",
        "Visiting Scholars"
    ]

    def sort_key(self, x):

        if x in ('Faculty',):
            return 0

        elif x in ('Staff',):
            return 1

        elif 'Faculty' in x:
            return 2

        elif 'Staff' in x:
            return 3

        elif 'Student' in x:
            return 5

        return 4

    # All classifications that exist as objects
    @property
    def directory_classifications(self):
        results = self.portal_catalog.searchResults({'Type' : 'Classification'})
        return [x.Title for x in results]

    # All classifications that are selected on people
    @property
    def used_classifications(self):
        _ = []

        results = self.portal_catalog.searchResults({
            'Type' : 'Person',
            'expires' : {
                'range' : 'min',
                'query' : DateTime(),
            }
        })

        for r in results:
            c = r.DirectoryClassification
            if c and isinstance(c, (list, tuple)):
                _.extend(c)

        return sorted(set(_))

    @property
    def items(self):

        _ = self.directory_classifications

        _.extend(self.defaults)

        # Alphabetical sort first
        _ = sorted(set(_))

        # Sort by faculty/staff second
        return sorted(_, key=self.sort_key)


# Directory groups for people
class PersonGroupsVocabulary(StaticVocabulary):

    @property
    def items(self):
        results = self.portal_catalog.searchResults({'Type' : 'DirectoryGroup'})
        return [x.Title for x in results]

# US States
class StatesVocabulary(KeyValueVocabulary):

    items = [
        ('PA', 'Pennsylvania'),
        ('AL', 'Alabama'),
        ('AK', 'Alaska'),
        ('AS', 'American Samoa'),
        ('AZ', 'Arizona'),
        ('AR', 'Arkansas'),
        ('CA', 'California'),
        ('CO', 'Colorado'),
        ('CT', 'Connecticut'),
        ('DE', 'Delaware'),
        ('DC', 'District of Columbia'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('GU', 'Guam'),
        ('HI', 'Hawaii'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('IA', 'Iowa'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('ME', 'Maine'),
        ('MH', 'Marshall Islands'),
        ('MD', 'Maryland'),
        ('MA', 'Massachusetts'),
        ('MI', 'Michigan'),
        ('FM', 'Micronesia'),
        ('MN', 'Minnesota'),
        ('MS', 'Mississippi'),
        ('MO', 'Missouri'),
        ('MT', 'Montana'),
        ('NE', 'Nebraska'),
        ('NV', 'Nevada'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NY', 'New York'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('MP', 'Northern Marianas'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PW', 'Palau'),
        ('PR', 'Puerto Rico'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VT', 'Vermont'),
        ('VI', 'Virgin Islands'),
        ('VA', 'Virginia'),
        ('WA', 'Washington'),
        ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'),
    ]

# Short Name
class ShortNameVocabulary(StaticVocabulary):

    @property
    def items(self):
        return self.portal_catalog.uniqueValuesFor('getId')

class ResearchAreasVocabulary(StaticVocabulary):

    items = [
        u"Advanced Agricultural and Food Systems",
        u"Biologically-Based Materials and Products",
        u"Community Resilience and Capacity",
        u"Environmental Resilience",
        u"Global Engagement",
        u"Integrated Health Solutions",
    ]

# Factories
PublicTagsVocabularyFactory = PublicTagsVocabulary()
AllPublicTagsVocabularyFactory = AllPublicTagsVocabulary()
PersonClassificationsVocabularyFactory = PersonClassificationsVocabulary()
PersonGroupsVocabularyFactory = PersonGroupsVocabulary()
StatesVocabularyFactory = StatesVocabulary()
ShortNameVocabularyFactory = ShortNameVocabulary()
ResearchAreasVocabularyFactory = ResearchAreasVocabulary()