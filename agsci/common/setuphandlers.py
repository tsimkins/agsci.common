# Catalog logic from http://maurits.vanrees.org/weblog/archive/2009/12/catalog

import logging
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.registry import field
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

# The profile id of your package:
PROFILE_ID = 'profile-agsci.common:default'

def add_catalog_indexes(context, logger=None, programs_profile=False):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('agsci.common')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = [
                ('Tags', 'KeywordIndex'),
                ('DegreeInterestArea', 'KeywordIndex'),
                ('DegreeCareer', 'KeywordIndex'),
                ('hasLeadImage', 'BooleanIndex'),
                ('DirectoryClassification', 'KeywordIndex'),
                ('DirectoryGroup', 'KeywordIndex'),
                ('ContentIssues', 'FieldIndex'),
                ('ContentErrorCodes', 'KeywordIndex'),
                ('exclude_from_robots', 'BooleanIndex'),
             ]

    # Programs site-specific indexes
    if programs_profile:
        wanted.append(
            ('County', 'KeywordIndex'),
        )

    indexables = []

    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)

    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)

# Create keys with a default initial value that can be changed, and not
# overridden by reinstalls.
def create_registry_keys(site, logger):
    registry = getUtility(IRegistry)

    keys = [
        (
            'agsci.common.ai_api_key',
            Record(field.TextLine(title=u'Activity Insight API Key')),
            u''
        ),
        (
            'agsci.common.department_id',
            Record(field.TextLine(title=u'Department Id')),
            u''
        ),
        (
            'agsci.common.global_public_tags',
            Record(field.Tuple(title=u'Global Public Tags', value_type=field.TextLine())),
            ()
        ),
        (
            'agsci.common.enhanced_public_tags',
            Record(field.Bool(title=u'Enhanced Public Tags')),
            False
        ),
    ]

    for (key, record, value) in keys:

        if key not in registry:
            record.value = value
            registry.records[key] = record
            logger.info("Added key %s" % key)
        else:
            logger.info("Key %s exists. Did not add." % key)

def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """

    site = context.getSite()

    # Determine if this is the 'programs profile'
    programs_profile = not not context.readDataFile('agsci.common.programs.marker.txt')

    if programs_profile:
        logger = context.getLogger('agsci.common.programs')
        add_catalog_indexes(site, logger, programs_profile=programs_profile)
        return

    # Only run step if a flag file is present
    if context.readDataFile('agsci.common.marker.txt') is None:
        return

    logger = context.getLogger('agsci.common')
    add_catalog_indexes(site, logger)
    create_registry_keys(site, logger)