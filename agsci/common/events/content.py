from plone.portlets.constants import CONTEXT_CATEGORY
from plone.app.portlets.portlets import navigation
from DateTime import DateTime
from plone.dexterity.utils import createContentInContainer
from plone.app.textfield.value import RichTextValue
from plone.event.interfaces import IEventAccessor
from plone.app.dexterity.behaviors import constrains
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

from ..utilities import localize, add_editors_group, get_portlet_assignment_manager, \
    get_portlet_mapping

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

def onEventsFolderCreate(context, event):

    # Calculate dates
    now = DateTime()
    start_date = DateTime() + 30
    end_date = start_date + 1.0/24

    # restrict what this folder can contain
    behavior = ISelectableConstrainTypes(context)
    behavior.setConstrainTypesMode(constrains.ENABLED)
    behavior.setImmediatelyAddableTypes(['Event'])
    behavior.setLocallyAllowedTypes(['Event', 'Collection'])

    # Create sample event and set publishing date to 01-01-YYYY
    item = createContentInContainer(
        context,
        "Event",
        id="sample",
        title="Sample Event",
        description="This is a sample Event",
        checkConstraints=False
    )

    item.text = RichTextValue(
        raw='<p>You may delete this item</p>',
        mimeType=u'text/html',
        outputMimeType='text/x-html-safe'
    )

    item.setEffectiveDate(now)

    acc = IEventAccessor(item)
    acc.start = localize(start_date)
    acc.end = localize(end_date)

    # create 'upcoming' collection

    if 'upcoming' not in context.objectIds():
        item = createContentInContainer(
            context,
            "Collection",
            id="upcoming",
            title='Upcoming Events',
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
                u'v': [u'Event']
            }
        ])

        item.setSort_on('start')

    # Set default page to the latest news collection
    context.setDefaultPage('upcoming')

def onSubsiteCreate(context, event, add_group=True):

    # Add group for subsite and set permissions
    if add_group:
        editors_group = add_editors_group(context)

    # Create News folder
    if 'news' not in context.objectIds():

        item = createContentInContainer(
            context,
            "agsci_blog",
            id="news",
            title="News",
            checkConstraints=False
        )

        onBlogCreate(item, event)

    # Create Events folder
    if 'events' not in context.objectIds():

        item = createContentInContainer(
            context,
            "Folder",
            id="events",
            title="Events",
            checkConstraints=False
        )

        onEventsFolderCreate(item, event)

    # Hide portlets
    left_column_manager = get_portlet_assignment_manager(context, 'plone.leftcolumn')
    right_column_manager = get_portlet_assignment_manager(context, 'plone.rightcolumn')

    left_column_manager.setBlacklistStatus(CONTEXT_CATEGORY, True)
    right_column_manager.setBlacklistStatus(CONTEXT_CATEGORY, True)

    # Set portlets
    left_column = get_portlet_mapping(context, 'plone.leftcolumn')

    left_navigation = navigation.Assignment(name=context.Title(),
                                            root_uid=context.UID(),
                                            currentFolderOnly = False,
                                            includeTop = True,
                                            topLevel = 0,
                                            bottomLevel = 3)

    left_column['navigation'] = left_navigation

    # Create homepage
    if 'front-page' not in context.objectIds():

        item = createContentInContainer(
            context,
            "agsci_homepage",
            id="front-page",
            title=context.Title(),
            checkConstraints=False
        )

        context.setDefaultPage('front-page')