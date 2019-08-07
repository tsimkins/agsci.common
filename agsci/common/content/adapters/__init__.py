from Acquisition import aq_base, aq_chain
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.interfaces import ICollection
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility

from agsci.common.content.behaviors.tags import ITags, ITagsRoot

class BaseAdapter(object):

    def __init__(self, context):
        self.context = context

class TagsAdapter(BaseAdapter):

    @property
    def tag_root(self):

        for _ in aq_chain(self.context):

            if ITagsRoot.providedBy(_):
                return _

            elif IPloneSiteRoot.providedBy(_):
                return

    @property
    def parent_object(self):

        tag_root = self.tag_root

        if hasattr(tag_root, 'getDefaultPage'):
            default_page_id = tag_root.getDefaultPage()

            if default_page_id in tag_root.objectIds():
                default_page = tag_root[default_page_id]

                if ICollection.providedBy(default_page):
                    return default_page

        return tag_root

    @property
    def available_tags(self):

        p = self.tag_root

        if p:
            v = getattr(p, 'available_public_tags', [])

            if v:
                return sorted(v)

        return []

    def normalize(self, _):
        normalizer = getUtility(IIDNormalizer)
        return normalizer.normalize(_)

    @property
    def normalized_tags(self):

        normalized_tags = []

        for _ in self.available_tags:
            normalized_tags.append([self.normalize(_), _])

        return dict(normalized_tags)


    @property
    def tags(self):
        return self.get_tags(self.context)

    def get_tags(self, o):

        if ITags.providedBy(o):

            _ = getattr(aq_base(o), 'public_tags', [])

            if _:
                return _

        return []

    @property
    def items(self):
        return self.get_items(self.available_tags)

    def get_items(self, tags):

        parent_object = self.parent_object
        path = '/'.join(self.tag_root.getPhysicalPath())

        if tags:

            if ICollection.providedBy(parent_object):

                return parent_object.results(
                    batch=False,
                    custom_query={
                        'Tags' : tags
                    }
                )

            else:

                return self.portal_catalog.searchResults({
                    'Tags' : tags,
                    'path' : path
                })

        return []


    @property
    def selected_tags(self):

        rv = []

        tags = []

        for _ in self.items:

            if _.Tags:

                tags.extend(_.Tags)

        tags = sorted(set(tags) & set(self.available_tags))

        for t in sorted(tags):
            rv.append([self.normalize(t), t])

        return rv

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

class LocationAdapter(BaseAdapter):

    @property
    def street_address(self):
        _ = getattr(self.context, 'street_address', [])

        if _ and isinstance(_, (tuple, list)):
            _ = [x for x in _ if x]
            return '<br />'.join(_)

    @property
    def has_address(self):
        return all([
            getattr(self.context, 'city', None),
            getattr(self.context, 'state', None),
            getattr(self.context, 'zip_code', None),
        ])