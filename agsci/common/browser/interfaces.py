from plone.theme.interfaces import IDefaultPloneLayer
from plone.app.contenttypes.interfaces import IPloneAppContenttypesLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.event.interfaces import IBrowserLayer

class IThemeSpecific(IDefaultPloneLayer):
    pass

class IThemeContentTypes(IPloneAppContenttypesLayer):
    pass

class IThemeBrowserLayer(IBrowserLayer):
    pass