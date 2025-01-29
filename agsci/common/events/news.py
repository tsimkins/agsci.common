from DateTime import DateTime
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from plone.app.dexterity.behaviors import constrains
from plone.app.portlets.portlets import navigation
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEventAccessor
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from agsci.common.content.blog import IBlog
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

def getParentBlog(context):

    for o in context.aq_chain:
        if IBlog.providedBy(o):
            return o
        if IPloneSiteRoot.providedBy(o):
            return

def getNewsExpirationDate(context):

    parent_blog = getParentBlog(context)
    
    # Skip if we don't have a parent blog
    if not parent_blog:
        return
    
    auto_expire = getattr(parent_blog.aq_base, 'auto_expire', True)
    auto_expire_months = getattr(parent_blog.aq_base, 'auto_expire_months', 60)

    # Skip if the auto_expire is not set on parent blog
    if not auto_expire:
        return

    auto_expire_days = int(auto_expire_months*(365.25/12.0))

    # Note that unset dates are in the year 2499, not None
    _effective_date = context.effective()
    _expiration_date = context.expires()

    _current = DateTime()

    # If it doesn't have an effective date, or it's more than the auto expiration 
    # period in the future, set the effective date to "now"
    if _effective_date > (_current+auto_expire_days):
        _effective_date = _current

    # Calculate the max expiration date based on the 
    max_expires = _effective_date + auto_expire_days

    # If the expiration date is not set, or further in the future than the calculated
    # max_expires, return max_expires
    if _expiration_date > max_expires:
        return max_expires

def setNewsExpirationDate(context, event):

    # Get the transition id
    try:
        action_id = event.action
    except AttributeError:
        return

    if action_id in ('publish', 'submit'):
    
        _expiration_date = getNewsExpirationDate(context)

        if _expiration_date:
            context.setExpirationDate(_expiration_date)
            context.reindexObject()
