from agsci.common import object_factory
from agsci.common.utilities import getExtensionConfig

from .. import BaseTile, ScooterTile

class JumbotronTile(BaseTile):
    __full_width__ = True

class RolloverPanelsTile(BaseTile):
    __full_width__ = True

class CallToActionImageAndBlocksTile(BaseTile):
    __full_width__ = True

class NewsAndEventsTile(BaseTile):

    @property
    def news(self):
        return self.get_items('target_news')[:3]

    @property
    def events(self):
        return self.get_items('target_events')[:3]

    @property
    def more_news_link(self):
        target_object = self.get_target_object('target_news')

        if target_object:

            parent = target_object.aq_parent

            if parent and parent.Type() in ['Blog',]:
                return parent.absolute_url()

            return target_object.absolute_url()

    @property
    def more_events_link(self):
        return self.get_more_items_link('target_events')

class ExtensionListingTile(ScooterTile):

    show_image_wrapper = True

    sku_order = []

    @property
    def config(self):
        return getExtensionConfig()

    def sku_sort_key(self, x):

        sku = x.sku

        if sku:

            try:
                return self.sku_order.index(sku)
            except:
                pass

        return 99999

    def to_brain(self, config=[]):
        rv = []

        for _ in config:
            # Present URL Key as SKU if no SKU for sorting/filtering purposes.
            __ = {
                'Title' : _.get('name', None),
                'Description' : _.get('description', None),
                'getURL' : _.get('url', None),
                'thumbnail' : _.get('thumbnail', None),
                'hasLeadImage' : not not _.get('thumbnail', None),
                'sku' : _.get('sku', _.get('url_key', None)),
            }

            rv.append(object_factory(**__))

        rv.sort(key=lambda x: x.Title)

        if self.sku_order:
            rv.sort(key=self.sku_sort_key)

        return rv

    def get_items(self):
        config = self.config

        if config:
            product_types = self.get_valid_value('product_types')

            if product_types:
                return self.to_brain([x for x in config if x.get('product_type', None) in product_types])

            return self.to_brain(config)

        return []

    def get_img_src(self, brain, **kwargs):
        return brain.thumbnail

class ExtensionFilteredListingTile(ExtensionListingTile):

    @property
    def department_id(self):
        return self.get_valid_value('department_id')

    @property
    def category(self):
        return self.get_valid_value('category')

    @property
    def config(self):
        return getExtensionConfig(
            department_id=self.department_id,
            category=self.category
        )

class ExtensionSKUFilteredListingTile(ExtensionFilteredListingTile):

    @property
    def sku_order(self):
        return self.get_valid_value('sku_order')

    @property
    def skus(self):
        return self.get_valid_value('skus')

    @property
    def config(self):
        _ = getExtensionConfig(
            department_id=self.department_id,
        )

        skus = self.skus

        # Filter by SKUs
        if skus:
            _ = [x for x in _ if x.get('sku', x.get('url_key', None)) in skus]

        return _