from DateTime import DateTime
from plone.dexterity.utils import createContentInContainer
from plone.app.textfield.value import RichTextValue

from ..utilities import localize

def onBlogCreate(context, event):

    # Calculate dates
    now = DateTime()

    # Create sample news item and set publishing date to 01-01-YYYY
    item = createContentInContainer(
        context,
        "News Item",
        id="sample",
        title="Sample News Item",
        description="This is a sample News Item",
        checkConstraints=False
    )

    item.text = RichTextValue(
        raw='<p>You may delete this item</p>',
        mimeType=u'text/html',
        outputMimeType='text/x-html-safe'
    )

    item.setEffectiveDate(now)

    # create 'latest' collection

    if 'latest' not in context.objectIds():
        item = createContentInContainer(
            context,
            "Collection",
            id="latest",
            title='Latest News',
        )

        item.setQuery([
            {
                u'i': u'path',
                u'o': u'plone.app.querystring.operation.string.absolutePath',
                u'v': u'%s::1' % context.UID()
            },
            {
                u'i': u'portal_type',
                u'o': u'plone.app.querystring.operation.selection.any',
                u'v': [u'News Item']
            }
        ])

        item.setSort_on('effective')

        item.setSort_reversed(True)

        setattr(item, 'show_date', True)

    # Set default page to the latest news collection
    context.setDefaultPage('latest')