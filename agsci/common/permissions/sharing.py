from zope.interface import implements, Interface
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore import permissions as core_permissions

try:
    from plone.app.workflow.interfaces import ISharingPageRole
except ImportError:
    # Fail nicely, this version of Plone doesn't know anything about @@sharing page roles.
    class ISharingPageRole(Interface):
        pass

class BaseRole(object):
    implements(ISharingPageRole)
    title = _(u"Base Role")
    required_permission = core_permissions.ManagePortal

class CollectionEditorRole(BaseRole):
    title = _(u"Collection Editor")

class RestrictedTypes(BaseRole):
    title = _(u"Restricted Types")