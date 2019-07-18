from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from .. import BaseTile, ConditionalTemplateTile

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
        return self.get_more_items_link('target_news')

    @property
    def more_events_link(self):
        return self.get_more_items_link('target_events')