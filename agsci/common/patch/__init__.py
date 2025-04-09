try:
    from plone.app.z3cform.widgets.patterns import TextareaWidget
except:
    from plone.app.widgets.base import TextareaWidget

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from xml.sax.saxutils import quoteattr
from zope.component import getMultiAdapter

from agsci.common.content.behaviors.leadimage import ILeadImage

def textarea_autocomplete(self, pattern, pattern_options={}, name=None, value=None):

    super(TextareaWidget, self).__init__('textarea', pattern,
                                            pattern_options)
    self.el.text = ''

    # Added autocomplete=off
    self.el.set('autocomplete', 'off')

    if name is not None:
        self.name = name
    if value is not None:
        self.value = value

def syndication_start(self):
    if hasattr(self.context, 'start'):
        date = self.context.start
        if date and date != 'None':
            return DateTime(date)

def syndication_public_tags(self):
    tags = getattr(self.context, 'public_tags', [])
    if tags and isinstance(tags, (list, tuple)):
        return list(tags)

def syndication_enclosure(self):
    lead = ILeadImage(self.context, None)
    if lead:
        if (lead.image
            and hasattr(lead.image, 'getSize')
            and lead.image.getSize() > 0):
            return u"""
                <enclosure
                    url="%s"
                    length="%d"
                    type="%s" />
            """ % (
                '%s/@@images/image/large' % self.context.absolute_url(),
                lead.image.getSize(),
                lead.image.contentType,
            )

def image_tag_from_values(*values):
    """Turn list of tuples into an img tag.

    Naturally, this should at least contain ("src", "some url").
    """
    parts = ["<img"]
    for k, v in values:
        # Skip width/height
        if k in ('width', 'height'):
            continue

        # Include alt text as blank string
        if k in ('alt',):
            if not v:
                v = ''

        if v is None:
            continue

        if isinstance(v, int):
            v = str(v)
        elif isinstance(v, bytes):
            v = str(v, "utf8")
        parts.append(f"{k}={quoteattr(v)}")

    parts.append("/>")

    return " ".join(parts)

def ploneview_showToolbar(self):
    """Determine if the editable border should be shown"""
    request = self.request
    if "disable_border" in request or "disable_toolbar" in request:
        return False
    if "enable_border" in request or "enable_toolbar" in request:
        return True

    context = aq_inner(self.context)

    portal_membership = getToolByName(context, "portal_membership")
    checkPerm = portal_membership.checkPermission

    if (
        checkPerm("Modify portal content", context)
        or checkPerm("Add portal content", context)
        or checkPerm("Review portal content", context)
        or checkPerm("Copy or Move", context)
    ):
        return True

    if portal_membership.isAnonymousUser():
        return False

    context_state = getMultiAdapter((context, request), name="plone_context_state")
    actions = context_state.actions

    if actions("workflow", max=1):
        return True

    if actions("batch", max=1):
        return True

    for action in actions("object"):
        if action.get("id", "") != "view":
            return True

    template_id = None
    if "PUBLISHED" in request:
        if getattr(request["PUBLISHED"], "getId", None):
            template_id = request["PUBLISHED"].getId()

    idActions = {}
    for obj in actions("object") + actions("folder"):
        idActions[obj.get("id", "")] = 1

    if "edit" in idActions:
        if template_id in idActions or template_id in [
            "synPropertiesForm",
            "folder_contents",
            "folder_listing",
            "listing_view",
        ]:
            return True

    # Check to see if the user is able to add content
    allowedTypes = context.allowedContentTypes()
    if allowedTypes:
        return True

    return False