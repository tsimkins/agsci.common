from Acquisition import aq_chain
from Products.CMFPlone.interfaces import IPloneSiteRoot

from agsci.common.content.behaviors.tags import ITagsRoot

class BaseAdapter(object):

    def __init__(self, context):
        self.context = context

class TagsRootAdapter(BaseAdapter):

    @property
    def tag_parent(self):

        for _ in aq_chain(self.context):

            if ITagsRoot.providedBy(_):
                return _

            elif IPloneSiteRoot.providedBy(_):
                return
    @property
    def available_tags(self):

        p = self.tag_parent

        if p:
            v = getattr(p, 'available_public_tags', [])

            if v:
                return sorted(v)

        return []
