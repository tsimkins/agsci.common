from bs4 import BeautifulSoup

from agsci.common import object_factory

class LinkReport(object):

    def __init__(self, context):
        self.context = context

    def __call__(self):
        _name = self.context.__name__
        _tile_type = self.context.tile_type

        for (_label, _url) in self.links:
            yield object_factory(
                name=_name,
                tile_type=_tile_type,
                label=_label,
                url=_url,
            )

class TextLinkReport(LinkReport):

    @property
    def text(self):

        _ = self.context.get_field('text')

        if _ and hasattr(_, 'raw'):
            yield _.raw

    @property
    def soup(self):
        return [BeautifulSoup(x, features="lxml") for x in self.text]

    @property
    def links(self):

        for soup in self.soup:

            for a in soup.findAll('a'):

                url = a.get('href', '')
                label = a.text

                if url:
                    yield (label, url)

class ValueTextLinkReport(TextLinkReport):

    @property
    def text(self):

        value = self.context.value

        if isinstance(value, (list, tuple)):

            for _ in value:

                if isinstance(_, (dict,)):

                    text = _.get('text', None)

                    if text and hasattr(text, 'raw'):
                        yield text.raw

class TitleLinkReport(LinkReport):

    title_field = 'title'

    @property
    def links(self):

        title = self.context.get_field(self.title_field, 'N/A')
        url = self.context.get_field('url', None)

        if url:
            yield (title, url)

class LabelLinkReport(TitleLinkReport):

    title_field = 'label'

class CTALinkReport(LinkReport):

    title_field = 'label'

    @property
    def links(self):

        value = self.context.value

        if isinstance(value, (list, tuple)):

            for _ in value:

                if isinstance(_, (dict,)):

                    title = _.get(self.title_field, 'N/A')
                    url = _.get('url', None)

                    if url:
                        yield (title, url)

class ButtonLinkReport(CTALinkReport):

    title_field = 'title'

class SocialMediaLinkReport(CTALinkReport):

    title_field = 'platform'


def link_factory(_):

    return {
        'agsci.common.tiles.animal' : [],
        'agsci.common.tiles.callout_block' : [TextLinkReport,],
        'agsci.common.tiles.cta' : [ButtonLinkReport, ],
        'agsci.common.tiles.dropdown_accordion' : [ValueTextLinkReport,],
        'agsci.common.tiles.explore_more' : [ValueTextLinkReport, ],
        'agsci.common.tiles.fozziebear' : [],
        'agsci.common.tiles.gonzo' : [TitleLinkReport, TextLinkReport,],
        'agsci.common.tiles.jumbotron' : [],
        'agsci.common.tiles.kermit' : [ButtonLinkReport, ],
        'agsci.common.tiles.large_cta' : [LabelLinkReport, TextLinkReport],
        'agsci.common.tiles.misspiggy' : [TextLinkReport,],
        'agsci.common.tiles.navigation' : [],
        'agsci.common.tiles.pepe_the_king_prawn' : [],
        'agsci.common.tiles.portlets' : [],
        'agsci.common.tiles.pull_quote' : [],
        'agsci.common.tiles.richtext' : [TextLinkReport,],
        'agsci.common.tiles.rizzo_the_rat' : [],
        'agsci.common.tiles.rowlf' : [LabelLinkReport,],
        'agsci.common.tiles.scooter' : [],
        'agsci.common.tiles.short_jumbotron' : [],
        'agsci.common.tiles.skeeter' : [],
        'agsci.common.tiles.social_media' : [SocialMediaLinkReport, ],
        'agsci.common.tiles.statler' : [ButtonLinkReport, ],
        'agsci.common.tiles.youtube' : [TitleLinkReport,],
    }.get(_, [])