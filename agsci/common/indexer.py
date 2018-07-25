from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from plone.namedfile.file import NamedBlobFile
from zope.component import provideAdapter

from .content.behaviors.tags import ITags
from .interfaces import ITagsAdapter

# Public Tags
@indexer(ITags)
def Tags(context):

    return ITagsAdapter(context).tags

provideAdapter(Tags, name='Tags')