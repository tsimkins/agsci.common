from Acquisition import aq_base
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from plone.namedfile.file import NamedBlobFile
from zope.component import provideAdapter

from .content.behaviors.tags import ITags
from .content.behaviors.leadimage import ILeadImage, LeadImage
from .content.degrees import IDegree

from .interfaces import ITagsAdapter

# Public Tags
@indexer(ITags)
def Tags(context):

    return ITagsAdapter(context).tags

provideAdapter(Tags, name='Tags')

# Public Tags
@indexer(ITags)
def Tags(context):

    return ITagsAdapter(context).tags

provideAdapter(Tags, name='Tags')

# Lead Image
@indexer(ILeadImage)
def hasLeadImage(context):
    return LeadImage(context).has_image

provideAdapter(hasLeadImage, name='hasLeadImage')

# Degree fields
degree_index_field =[
    ('DegreeInterestArea', 'interest_area'),
    ('DegreeCareer', 'career'),
    ('DegreeEmployer', 'employer'),
    ('DegreeClub', 'club'),
    ('DegreeFacility', 'facility'),
    ('DegreeScholarship', 'scholarship'),
]

# Function that returns a "get a value of this field" function
def degree_indexer(i):

    @indexer(IDegree)
    def f(context):
        v = getattr(aq_base(context), i, [])

        if v:
            return v
        return []

    return f

# Create indexers for each degree field
for (_idx, _field) in degree_index_field:
    f = degree_indexer(_field)
    provideAdapter(f, name=_idx)