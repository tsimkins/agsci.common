from Acquisition import aq_base
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from plone.namedfile.file import NamedBlobFile
from zope.component import provideAdapter

from .content.behaviors import IAlwaysExcludeFromNavigation, ISEO
from .content.behaviors.tags import ITags
from .content.behaviors.leadimage import ILeadImage, LeadImage
from .content.check import getValidationErrors
from .content.degrees import IDegree
from .content.person.person import IPerson

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

# Person Sortable Title
@indexer(IPerson)
def PersonSortableTitle(context):
    try:
        return context.getSortableName()
    except:
        return ('Z', 'Z')

provideAdapter(PersonSortableTitle, name='sortable_title')

# Person Sortable Title
@indexer(IPerson)
def PersonLastFirst(context):
    try:
        return context.getLastFirstName()
    except:
        return ''

provideAdapter(PersonLastFirst, name='sortable_title_case')

# Person Directory Classification
@indexer(IPerson)
def PersonDirectoryClassification(context):
    try:
        return getattr(context.aq_base, 'classifications', [])
    except:
        return []

provideAdapter(PersonDirectoryClassification, name='DirectoryClassification')

# Person Directory Group
@indexer(IPerson)
def PersonDirectoryGroup(context):
    try:
        return getattr(context.aq_base, 'groups', [])
    except:
        return []

provideAdapter(PersonDirectoryGroup, name='DirectoryGroup')

@indexer(IAlwaysExcludeFromNavigation)
def AlwaysExcludeFromNavigation(context):
    return True

provideAdapter(AlwaysExcludeFromNavigation, name='exclude_from_nav')

# Content Error Codes
@indexer(IDexterityContent)
def ContentErrorCodes(context):
    errors = getValidationErrors(context)
    return tuple(sorted(set([x.error_code for x in errors])))

provideAdapter(ContentErrorCodes, name='ContentErrorCodes')

# Content Issues
@indexer(IDexterityContent)
def ContentIssues(context):
    return len([x for x in getValidationErrors(context)])

provideAdapter(ContentIssues, name='ContentIssues')

# Exclude From Robots
@indexer(ISEO)
def exclude_from_robots(context):
    return not not getattr(context.aq_base, 'exclude_from_robots', False)

provideAdapter(exclude_from_robots, name='exclude_from_robots')