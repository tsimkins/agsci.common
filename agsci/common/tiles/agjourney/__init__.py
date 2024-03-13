from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from .. import BaseTile, ConditionalTemplateTile, YouTubeTile, JumbotronTile

class AgJourneyJumbotronTile(JumbotronTile):

    __full_width__ = True

class AgJourneyBioTile(YouTubeTile):

    image_scale = 'large'

class QuoteAndImageTile(ConditionalTemplateTile):

    __full_width__ = True

    image_scale = 'large'

    @property
    def padding(self):
        _ = []

        if self.get_valid_value('padding_top'):
            _.append('pt-3')

        if self.get_valid_value('padding_bottom'):
            _.append('pb-3')

        if self.get_valid_value('style') in ('handwriting_large',):
            _.append('px-0')

        return _

    @property
    def section_class(self):
        _ = "container-fluid bg-light-gray".split()

        _.extend(self.padding)

        return " ".join(_)

    @property
    def style(self):
        return self.get_valid_value('style')

    @property
    def render_template(self):
        return ViewPageTemplateFile('templates/%s' % self.template)

    @property
    def template(self):
        return 'quote_%s.pt' % self.style
