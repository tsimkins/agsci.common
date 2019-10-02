from plone.dexterity.utils import createContentInContainer

from agsci.common.content.person import LDAPInfo

from .. import ImportContentView

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