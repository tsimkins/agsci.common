from plone.app.widgets.base import TextareaWidget
from DateTime import DateTime

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