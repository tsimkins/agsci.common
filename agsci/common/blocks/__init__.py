from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from zope.component.hooks import getSite
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest

import json

from ..utilities import toBool

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

        html = el.encode_contents()
        html = safe_unicode(html)
        return template.render(html=html, view=self, **data)

    @property
    def portal_catalog(self):
        return getToolByName(self.site, 'portal_catalog')

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
        'full' : False,
    }

class PersonBlock(BaseBlock):
    template = 'person.j2'

    defaults = {
        'count' : 2,
    }

    def toBool(self, _):
        return toBool(_)

    def card_view(self, r, style=None, border=True):
        o = r.getObject()

        if style == 'vertical':

            if not border:
                return o.restrictedTraverse('@@card_view_vertical_no_border')()

            return o.restrictedTraverse('@@card_view_vertical_image')()

        return o.restrictedTraverse('@@card_view_image')()

    def people(self, usernames, style=None, border=True):

        _ids = [x.strip() for x in usernames.split(',')]

        if _ids:

            results = self.portal_catalog.searchResults({
                'Type' : 'Person',
                'getId' : _ids,
                'sort_on' : 'sortable_title',
            })

            return [self.card_view(x, style, toBool(border)) for x in results]

        return []

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

class BorderedCalloutBlock(BaseBlock):
    template = 'bordered-callout.j2'

    defaults = {
        'reveal' : 'reveal',
    }
