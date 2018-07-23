from Acquisition import aq_chain
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getUtility, getUtilitiesFor
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements

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

    def tag_parent(self, context):

        for o in aq_chain(context):
    
            if ITagsRoot.providedBy(o):
                return context
    
            elif IPloneSiteRoot.providedBy(o):
                return
    
    def items(self, context):

        p = self.tag_parent(context)
        
        if p:
            v = getattr(p, 'available_public_tags', [])
            
            if v:
                return sorted(v)
        
        return []

    def __call__(self, context):
    
        items = self.items(context)
        
        return SimpleVocabulary(
            [
                SimpleTerm(x, title=x) for x in items
            ]
        )

        return []

# Factories
PublicTagsVocabularyFactory = PublicTagsVocabulary()

