from DateTime import DateTime
from bs4 import BeautifulSoup
from datetime import datetime
from plone.app.textfield.value import RichTextValue

import requests
import transaction

from agsci.common.browser.views import BaseView
from agsci.common.content.person.directory import IPersonPublicationListing
from agsci.common.utilities import localize

from .. import ImportContentView

class ImportDirectoryPublicationsView(ImportContentView):

    roles = ['Contributor', 'Reader', 'Editor', 'Member', 'Directory Editor']

    api_key_id = 'agsci.common.ai_api_key'

    years = 5

    # Start date of publications to show. Includes anything published after 1/1
    # because the publication date isn't always precise.
    @property
    def min_pub_date(self):
        _ = DateTime() - (365.25*self.years)
        _ = DateTime('%d-01-01' % _.year())
        return localize(_)

    # Sorts the publication data by date, and filters by year
    def sort_filter(self, data=[]):

        min_pub_date = self.min_pub_date

        data = sorted(data, key=lambda x: x.get('published_on', None), reverse=True)

        # Filter by a minimum date to ensure only recent ones are returned
        return [
            x for x in data \
            if x.get('published_on', None) and \
            isinstance(x['published_on'], datetime) and \
            x['published_on'] >= min_pub_date
        ]

    @property
    def api_key(self):
        return self.registry.get(self.api_key_id, None)

    def get_api_data(
        self,
        url,
        params=[],
        method='GET',
        format='json',
        body={},
    ):
        api_key = self.api_key
        api_host = "https://metadata.libraries.psu.edu"
        api_url = "".join([api_host, url % params])

        if not api_key:
            raise Exception('%s not set in registry.' % self.api_key_id)

        headers = {'X-API-Key' : api_key}

        if format.lower() in 'json':
            headers['Accept'] = 'application/json'

        if method.upper() in ('POST',):
            response = requests.post(
                api_url,
                headers = headers,
                json=body,
            )

        else:
            response = requests.get(
                api_url,
                headers = headers
            )

        if response.status_code not in (200,):
            raise Exception('Error getting data for %s' % api_url)

        if format.lower() in 'json':
            return response.json()

        return response.text

    def get_publications_html(self, user_id):

        pubs_api_url = "/v1/users/%s/publications"
        publications = self.get_api_data(pubs_api_url, user_id, format='html')
        soup = BeautifulSoup(publications, features="lxml")
        soup.html.hidden = True
        soup.body.hidden = True
        return unicode(soup.find('ul'))

    def get_publications_json(self, user_id):

        pubs_api_url = "/v1/users/%s/publications"
        data = self.get_api_data(pubs_api_url, user_id)

        if isinstance(data, dict):

            return data.get('data', [])

        return []

    def get_publications(self, user_id):

        profile = self.get_profile(user_id)
        return profile.get('data', {}).get('attributes', {}).get('publications', [])

    @property
    def publications(self):

        org_api_url = "/v1/organizations"
        pubs_api_url = "/v1/organizations/%s/publications"

        organizations = self.get_api_data(org_api_url)

        org_ids = [
            x.get('id', None)
            for x in organizations.get('data', [])
            if x.get('type', None) in ('organization',)
        ]

        for _id in org_ids:
            return self.get_api_data(pubs_api_url, _id)

    @property
    def people(self):
        return self.portal_catalog.searchResults({
            'Type' : 'Person',
            'DirectoryClassification' : ['Faculty', 'Staff'],
            'review_state' : 'published',
            'expires' : {
                'range' : 'min',
                'query' : DateTime()
            }
        })

    def get_profile(self, user_id):

        profile_api_url = "/v1/users/%s/profile"
        return self.get_api_data(profile_api_url, user_id)

    def import_content(self):

        for r in self.people:
            o = r.getObject()

            # Skip faculty who have a profile outside the department
            if not getattr(o, 'primary_profile_url', None):

                v = ImportPersonPublicationsView(o, self.request)

                try:
                    v()
                except:
                    self.log("Error importing publications for %s" % r.getURL())
                else:
                    self.log("Successfully imported publications for %s" % r.getURL())

class ImportPersonPublicationsView(ImportDirectoryPublicationsView):

    years = 10

    def import_content(self):

        username = getattr(self.context, 'username', None)

        if username:
            try:
                data = self.get_publications_json(username)
            except:
                pass
            else:
                if data and isinstance(data, (list, tuple)):
                    publications = []

                    for __ in data:

                        _ = __.get('attributes', {})

                        contributors = [
                            "%s, %s" % (
                                x.get('last_name', ''),
                                x.get('first_name', ''),
                            ) for x in _.get('contributors', [])
                            if x.get('last_name', '')
                        ]

                        try:
                            published_on = localize(
                                DateTime("%s 00:00:00 US/Eastern" % _['published_on'])
                            )
                        except:
                            published_on = None

                        abstract = _.get('abstract', None)

                        if abstract:
                            abstract = RichTextValue(
                                raw=abstract,
                                mimeType=u'text/html',
                                outputMimeType='text/x-html-safe'
                            )

                        publications.append({
                            'ai_id' : __.get('id', None),
                            'title' : _.get('title', None),
                            'doi' : _.get('doi', None),
                            'journal_title' : _.get('journal_title', None),
                            'published_on' : published_on,
                            'abstract' : abstract,
                            'contributors' : contributors,
                        })

                    self.context.publications = self.sort_filter(publications)
                    self.context.reindexObject()
                    transaction.commit()

                    self.log(u"Imported %d publications for %s" % (len(publications), username))

class ImportSitePublicationsView(ImportDirectoryPublicationsView):

    # people is a list of *objects* not brains
    def get_publications_for_people(self, people=[]):

        data = {}

        for o in people:

            # Skip faculty who have a profile outside the department
            if not getattr(o, 'primary_profile_url', None):

                publications = getattr(o, 'publications', [])

                if publications and isinstance(publications, (list, tuple)):

                    for _ in publications:
                        if isinstance(_, dict):
                            _id = _.get('ai_id', None)

                            if _id and _id not in data:
                                data[_id] = _

        return self.sort_filter(data.values())

    @property
    def publication_listings(self):
        results = self.portal_catalog.searchResults({
            'object_provides' : 'agsci.common.content.person.directory.IPersonPublicationListing',
        })

        _ = [x.getObject() for x in results]

        try:
            context = self.site.restrictedTraverse('research/publications')
        except:
            pass
        else:
            _.append(context)

        if not _:
            self.log(u"No research publications page found.")

        return _


    def import_content(self):

        v = BaseView(self.context, self.request)

        for context in self.publication_listings:

            self.log(u"Populating publications listing for %s." % context.absolute_url())

            people = []

            # People Publication listing specifies people
            if IPersonPublicationListing.providedBy(context):
                people = context.people()

            # All people
            else:
                people = [x.getObject() for x in self.people]

            if people:

                publications = self.get_publications_for_people(people)

                if publications:

                    html = v.publications_html(publications=publications)

                    context.text = RichTextValue(
                        raw=html,
                        mimeType=u'text/html',
                        outputMimeType='text/x-html-safe'
                    )

                    context.reindexObject()

                    transaction.commit()