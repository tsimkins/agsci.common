from plone.app.portlets.portlets import base
from zope.component import queryMultiAdapter

class TilePortletAssignment(base.Assignment):

    title = ''

    def __init__(self, title=title, *args, **kwargs):
        base.Assignment.__init__(self, *args, **kwargs)
        self.title=title

class TilePortletRenderer(base.Renderer):

    tile_name = ''

    @property
    def tile(self):
        return queryMultiAdapter((self.context, self.request), name=self.tile_name)

    def render(self):

        tile = self.tile

        if tile:

            # Push data into our custom tiles
            try:
                tile.set_data(self.data)
            except:
                pass

            return tile()