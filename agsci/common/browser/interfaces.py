from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer

class IThemeSpecific(IDefaultPloneLayer):
    pass

class IThemeContentTypes(IPloneAppContenttypesLayer):
    pass