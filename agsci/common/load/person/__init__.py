from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage
from zLOG import LOG, INFO, ERROR
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from agsci.common.constants import DOMAIN_CONFIG
from agsci.common.content.person import LDAPInfo
from agsci.common.indexer import PersonSortableTitle
from agsci.common.utilities import ploneify, md5sum

from .. import ImportContentView, ContentImporter

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import json

class SyncPersonView(ImportContentView):

    @property
    def api_domains(self):
        return sorted(set([x.lower() for x in DOMAIN_CONFIG.values()]))

    @property
    def primary_profile_url(self):
        return getattr(self.context, 'primary_profile_url', None)

    @property
    def api_url(self):
        url = self.primary_profile_url

        if url:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path

            if domain.lower() in self.api_domains:
                return 'https://%s%s/@@dump-json' % (domain, path)

    def cmp(self, _1, _2):

        def to_json(x):
            try:
                return json.dumps(x, sort_keys=True)
            except:
                return None

        # If both are empty, they're the same, even if they're not literally the same.
        # This prevents a None and '' mismatch.
        if not _1 and not _2:
            return True

        return to_json(_1) == to_json(_2)

    def blob_md5sum(self, context, field='image'):

        blob = getattr(context, field, None)

        if isinstance(blob, NamedBlobImage) and hasattr(blob, 'data') and blob.data:
            return md5sum(blob.data)

    # Check for updates to person data
    def update_person(self, o, include_fields=[]):

        update = False

        # Explicitly included fields
        for _ in include_fields:
            _1 = getattr(self.context.aq_base, _, None)
            _2 = getattr(o.data, _, None)

            if _2 and not self.cmp(_1, _2):

                LOG(
                    self.__class__.__name__, INFO,
                    "%s: Update %s %r to %r" % (
                        self.context.absolute_url(),
                        _,
                        _1,
                        _2
                    )
                )

                update = True

        # Check for image differences
        image_md5sum = self.blob_md5sum(self.context.aq_base)
        api_image_md5sum = self.blob_md5sum(o)

        if api_image_md5sum and api_image_md5sum != image_md5sum:
            update = True

            LOG(
                self.__class__.__name__, INFO,
                "%s: Update image %r to %r" % (
                    self.context.absolute_url(),
                    image_md5sum,
                    api_image_md5sum
                )
            )

        return update

    def import_content(self):
        api_url = self.api_url

        if api_url:

            path = "/".join(self.context.getPhysicalPath())
            uid = self.context.UID()

            include_fields = [
                u'areas_expertise',
                u'first_name',
                u'middle_name',
                u'last_name',
                u'suffix',
                u'email',
                u'phone_number',
                u'job_titles',
                u'street_address',
                u'city',
                u'state',
                u'zip_code'
            ]

            o = ContentImporter(
                path,
                UID=uid,
                api_url=api_url,
                include_fields=include_fields,
                debug=True,
                map_fields=False,
            )

            LOG(
                self.__class__.__name__, INFO,
                "Checking %s for updates" % (
                    self.context.absolute_url(),
                )
            )

            if self.update_person(o, include_fields):
                o(force=True)
        else:
            LOG(
                self.__class__.__name__, INFO,
                "Skipping %s" % (
                    self.context.absolute_url(),
                )
            )

class SyncDirectoryView(ImportContentView):

    def import_content(self):

        for o in self.context.people():
            v = o.restrictedTraverse('@@sync_person')
            v()

class ImportPersonView(ImportContentView):

    @property
    def username(self):
        return self.request.get('username', None)

    def create_person(self, **kwargs):

        context = self.directory

        item = createContentInContainer(
            context,
            "agsci_person",
            id=self.username,
            username=self.username,
            checkConstraints=False,
            **kwargs
        )

        item.reindexObject()

        return item

    def import_content(self):

        if self.username:

            if self.username in self.directory.objectIds():
                raise ValueError("%s already in directory." % self.username)

            ldap = LDAPInfo(self.directory, self.username)

            _ = ldap.lookup()

            if not _:
                raise ValueError("%s not found in LDAP." % self.username)

            (street_address, city, state, zip_code) = ldap.get_address(_)

            if street_address:
                street_address = [street_address,]

            job_titles = []

            job_title = _.get('title', None)

            if job_title:
                job_titles.append(job_title)

            kwargs = {
                'last_name' : _.get('sn', None),
                'first_name' : _.get('givenName', None),
                'street_address' : street_address,
                'city' : city,
                'state' : state,
                'zip_code' : zip_code,
                'email' : _.get('mail', None),
                'phone_number' : ldap.get_phone_number(_),
                'job_titles' : job_titles
            }

            item = self.create_person(**kwargs)

            RESPONSE =  self.request.RESPONSE

            RESPONSE.setHeader(
                'Cache-Control',
                'max-age=0, s-maxage=3600, must-revalidate, public, proxy-revalidate'
            )

            return RESPONSE.redirect(item.absolute_url())

        raise ValueError("No username provided")


    @property
    def directory(self):

        # Grab the directory, and do some sanity checks before jumping to LDAP
        site = self.site

        directory_type = "Directory"

        if 'directory' not in site.objectIds():
            raise KeyError("%s not found." % directory_type)

        context = site['directory']

        if context.Type() != directory_type:
            raise TypeError("Directory portal_type of %s not %s"  % (context.portal_type, directory_type))

        return context

class ImportClassificationsView(ImportPersonView):

    vocabulary_name = "agsci.common.person.classifications"

    group_order = [
        'Faculty',
        'Adjunct Faculty',
        'Affiliate Faculty',
        'Emeritus Faculty',
        'Instructors',
        'Researchers',
        'Post-Doctoral Scholars',
        'Visiting Scholars',
        'Staff',
        'Graduate Students',
        'Undergraduate Students',
    ]

    @property
    def vocabulary_factory(self):
        return getUtility(IVocabularyFactory, self.vocabulary_name)

    @property
    def missing_classifications(self):
        vocab = self.vocabulary_factory

        # Classificationis that physically exist
        directory_classifications = vocab.directory_classifications

        # Classifications that are actually used
        used_classifications = vocab.used_classifications

        # Classifications that are used, but don't physically exist
        _ = set(used_classifications) - set(directory_classifications)

        # Intersection with valid vocabulary items
        return list(_ & set(vocab.items))

    def create_classification(self, **kwargs):

        title = kwargs.get('title', None)

        if title:
            _id = ploneify(title)

            context = self.directory

            if _id not in context.objectIds():

                item = createContentInContainer(
                    context,
                    "agsci_directory_classification",
                    id=_id,
                    exclude_from_nav=False,
                    checkConstraints=False,
                    **kwargs
                )

                item.reindexObject()

                return item

    def reorder_directory(self):

        def sort_key(x):
            if x.Title() in self.group_order:
                return self.group_order.index(x.Title())

            return 99999

        groups = self.directory.listFolderContents({
            'Type' : [
                'Classification',
                'Person Listing',
                'DirectoryGroup',
            ]
        })

        groups.sort(key=sort_key)

        people = self.directory.listFolderContents({
            'Type' : [
                'Person',
            ]
        })

        people.sort(key=lambda x: x.getSortableName())

        group_ids = [x.getId() for x in groups]
        people_ids = [x.getId() for x in people]

        _ids = []
        _ids.extend(group_ids)
        _ids.extend(people_ids)

        for i in range(0, len(_ids)):
            self.directory.moveObjectToPosition(_ids[i], i)

    def import_content(self):

        rv = []

        for _ in self.missing_classifications:
            item = self.create_classification(title=_)

            if item:
                rv.append([_, item.absolute_url()])

        # Pull classifications and person listings to the top
        self.reorder_directory()

        if rv:
            return "Created %s" % json.dumps(rv, indent=4)

        return "No missing classifications"