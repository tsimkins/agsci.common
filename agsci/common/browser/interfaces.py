from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from plone.app.event.interfaces import IBrowserLayer
from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    pass

class IThemeContentTypes(IPloneAppContenttypesLayer):
    pass

class IThemeBrowserLayer(IBrowserLayer):
    pass