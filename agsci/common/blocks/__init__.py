from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from zope.component.hooks import getSite
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest

import json

class BaseBlock(object):

    template_base = '++resource++agsci.common.blocks/'
    template = 'base.j2'

    defaults = {}

    @property
    def site(self):
        return getSite()

    @property
    def request(self):
        return getRequest()

    def __init__(self, context):
        self.context = context

    def get_data(self, **kwargs):
        _ = dict(self.defaults)
        _.update(kwargs)
        return _

    def __call__(self, el, **kwargs):
        rendered = self.render(el, **kwargs)

        if rendered:
            soup = BeautifulSoup(rendered, features="lxml")
            soup.html.hidden = True
            soup.body.hidden = True

            # Remove tile wrapper sections
            for section in soup.findAll('section', attrs={'data-tile-type' : True}):
                section.hidden = True

            return soup

        return "<h2>NOTHING HERE</h2>"

    def render(self, el, **kwargs):
        resource = self.site.restrictedTraverse(self.template_base)

        loader = FileSystemLoader(resource.context.path)

        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template(
            self.template
        )

        data = self.get_data(**kwargs)

        return template.render(html=el.encode_contents(), view=self, **data)

class TileBlock(BaseBlock):

    tile_name = ''

    @property
    def tile(self):
        return queryMultiAdapter((self.site, self.request), name=self.tile_name)

    def render(self, el, **kwargs):
        tile = self.tile

        if tile:

            # Push data into our custom tiles
            try:
                tile.set_data(self.get_data(**kwargs))
            except:
                pass

            return tile()


class StatBlock(BaseBlock):
    template = 'stat.j2'

    defaults = {
        'align' : 'left'
    }

class CTABlock(BaseBlock):
    template = 'cta.j2'

    defaults = {
        'align' : 'left',
        'color' : 'purple',
    }

class PersonBlock(TileBlock):
    tile_name = 'agsci.common.tiles.animal'

    defaults = {
        'count' : 3,
        'style' : 'vertical',
    }

    def get_data(self, **kwargs):

        _ = super(PersonBlock, self).get_data(**kwargs)

        _['value'] = [{'username' : x.strip()} for x in kwargs.get('usernames', '').split(',')]

        return _

class HorizontalPersonBlock(PersonBlock):

    defaults = {
        'count' : 2,
        'style' : 'horizontal',
    }


class ShadowBoxBlock(BaseBlock):
    template = 'shadow-box.j2'

    defaults = {
        'align' : 'right',
    }

class YouTubeBlock(TileBlock):
    tile_name = 'agsci.common.tiles.youtube'

    defaults = {
        'aspect' : '16:9',
    }