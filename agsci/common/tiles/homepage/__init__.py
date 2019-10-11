from .. import BaseTile

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