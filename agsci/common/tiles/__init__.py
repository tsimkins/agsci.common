from plone import api
from plone import tiles

from .. import object_factory

class TestTile(tiles.PersistentTile):

    def can_edit(self):
        if api.user.is_anonymous():
            return False
        current = api.user.get_current()
        return api.user.has_permission(
            'Edit',
            username=current.id,
            obj=self.context)

    def klass(self):
    
        _ = [
            (4, 'mosaic-width-quarter'),
            (3, 'mosaic-width-third'),
            (2, 'mosaic-width-half'),
        ]
    
        values = [x for x in self.values]
        
        if values:

            value_count = len(values)
            
            for (v,k) in _:
                if not value_count % v:
                    return k

            # Default largest
            if value_count > _[0][0]:
                return _[0][1]
                
        return 'mosaic-width-full'
        
    @property
    def values(self):
        headings = ['title', 'description', 'link'] 

        values = self.data.get('values', [])
        
        if values:

            for _ in values:
                values = [x.strip() for x in _.split('|')]
                kwargs = dict(zip(headings, values))
                yield object_factory(**kwargs)
