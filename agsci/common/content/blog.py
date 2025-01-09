from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

@provider(IFormFieldProvider)
class IBlog(model.Schema):

    auto_expire = schema.Bool(
        title=_(u"Auto-Expire News Items"),
        description=_(u"Automatically set expiration date for news items inside this blog."),
        required=False,
        default=True,
    )

    auto_expire_months = schema.Int(
        title=_(u"Auto-Expire News Item Months"),
        description=_(u"Number of months to keep news items."),
        required=False,
        default=60,
    )

class Blog(Container):
    pass
