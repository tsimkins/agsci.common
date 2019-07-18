from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from .. import BaseTile, ConditionalTemplateTile

class JumbotronTile(BaseTile):
    __full_width__ = True

class RolloverPanelsTile(BaseTile):
    __full_width__ = True

class CallToActionImageAndBlocksTile(BaseTile):
    __full_width__ = True