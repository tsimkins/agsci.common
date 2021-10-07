from zope.annotation.interfaces import IAnnotations
from agsci.common.content.check import TileLinksCheck

# Provides easy access to tiles and settings for automation
# Remember to do a:
#
#    from agsci.common.tiles.interfaces import IAgsciTilesLayer
#    directlyProvides(app.REQUEST, IAgsciTilesLayer)


class TileUtility(object):

    def __init__(self, context):
        self.context = context


    # Provides a list of tiles associated with this page
    @property
    def tiles(self):
        return [x for x in TileLinksCheck(self.context).tiles]

    # List of tile types
    @property
    def tile_types(self):
        return [x.tile_type for x in self.tiles if hasattr(x, 'tile_type')]

    # Get all tiles by type
    def get_tiles(self, _type):
        return [x for x in self.tiles if hasattr(x, 'tile_type') and x.tile_type==_type]

    # Get a specific tile by type and index
    def get_tile(self, _type, _idx=0):

        _tiles = self.get_tiles(_type)

        if _tiles and len(_tiles) > _idx:
            return _tiles[_idx]

    def get_tile_data(self, _tile):
        tile_data = IAnnotations(self.context)
        tile_id = _tile.id
        tile_key = 'plone.tiles.data.%s' % tile_id

        if tile_key in tile_data:
            return tile_data[tile_key]

    def set_tile(self, _tile, **kwargs):

        tile_data = IAnnotations(self.context)
        tile_id = _tile.id
        tile_key = 'plone.tiles.data.%s' % tile_id

        if tile_key in tile_data:
            tile_data[tile_key].update(kwargs)
        else:
            tile_data[tile_key] = kwargs