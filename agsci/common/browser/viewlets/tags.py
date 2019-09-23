from agsci.common import object_factory
from agsci.common.interfaces import ITagsAdapter

from . import ViewletBase

class TagsViewlet(ViewletBase):

    target_view = "tags"

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
        return self.tags and isinstance(self.tags, (list, tuple)) and len(self.tags) > 1