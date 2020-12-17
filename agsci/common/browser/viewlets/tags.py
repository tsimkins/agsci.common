from agsci.common import object_factory
from agsci.common.interfaces import ITagsAdapter

from . import ViewletBase

class TagsViewlet(ViewletBase):

    target_view = "tags"

    viewlet_id = "public-tags"
    viewlet_title = "Filter by Tag"
    show_link = True
    min_tags = 2

    @property
    def adapted(self):
        return ITagsAdapter(self.context)

    @property
    def tags(self):
        return self.adapted.selected_tags

    @property
    def tag_data(self):
        return [
            object_factory(
                key=x[0],
                value=x[1]
            ) for x in self.tags
        ]

    @property
    def parent_object(self):
        return self.adapted.parent_object

    @property
    def tag_root(self):
        return self.adapted.tag_root

    @property
    def available(self):
        return self.tags and isinstance(self.tags, (list, tuple)) and len(self.tags) >= self.min_tags

class InternalTagsViewlet(TagsViewlet):

    viewlet_id = "internal-tags"
    viewlet_title = "Internal Tags"
    show_link = False
    min_tags = 1

    @property
    def tag_data(self):
        return [
            object_factory(
                key=x,
                value=x
            ) for x in self.tags
        ]

    @property
    def tags(self):
        if hasattr(self.context, 'Subject') and hasattr(self.context.Subject, '__call__'):
            return self.context.Subject()

class PublicTagsViewlet(InternalTagsViewlet):

    viewlet_id = "public-tags-item"
    viewlet_title = "Tags"

    @property
    def enhanced_public_tags(self):
        return not not self.registry.get('agsci.common.enhanced_public_tags')

    @property
    def tags(self):
        _ = getattr(self.context.aq_base, 'public_tags', None)
        if _ and isinstance(_, (list, tuple)):
            return sorted(_)

    @property
    def available(self):
        if self.enhanced_public_tags:
            return super(PublicTagsViewlet, self).available