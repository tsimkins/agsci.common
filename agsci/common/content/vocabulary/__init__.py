from Acquisition import aq_chain
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility, getUtilitiesFor
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements

from agsci.common.interfaces import ITagsAdapter

from ..behaviors.tags import ITagsRoot

class BaseVocabulary(object):

    implements(IVocabularyFactory)

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

# Directory classifications for people
class PersonClassificationsVocabulary(StaticVocabulary):

    items = [
        'Faculty',
        'Educator',
        'Staff',
        'Graduate Student',
    ]

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


# Factories
PublicTagsVocabularyFactory = PublicTagsVocabulary()
PersonClassificationsVocabularyFactory = PersonClassificationsVocabulary()
StatesVocabularyFactory = StatesVocabulary()