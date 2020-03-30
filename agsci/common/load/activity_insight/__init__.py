from DateTime import DateTime
from bs4 import BeautifulSoup
from plone.app.textfield.value import RichTextValue

import requests
import transaction

from agsci.common.browser.views import BaseView
from agsci.common.utilities import localize

from .. import ImportContentView

class ImportDirectoryPublicationsView(ImportContentView):

    api_key_id = 'agsci.common.ai_api_key'

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
    def faculty(self):
        return self.portal_catalog.searchResults({
            'Type' : 'Person',
            'DirectoryClassification' : 'Faculty',
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

        for r in self.faculty:
            o = r.getObject()

            v = ImportPersonPublicationsView(o, self.request)

            try:
                v()
            except:
                self.log("Error importing publications for %s" % r.getURL())
            else:
                self.log("Successfully imported publications for %s" % r.getURL())

class ImportPersonPublicationsView(ImportDirectoryPublicationsView):

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
                        })

                    self.context.publications = sorted(publications, key=lambda x: x.get('published_on'), reverse=True)
                    self.context.reindexObject()
                    transaction.commit()

                    self.log(u"Imported %d publications for %s" % (len(publications), username))

class ImportSitePublicationsView(ImportDirectoryPublicationsView):

    @property
    def publications(self):

        data = {}

        for r in self.faculty:
            o = r.getObject()

            publications = getattr(o, 'publications', [])

            if publications and isinstance(publications, (list, tuple)):

                for _ in publications:
                    if isinstance(_, dict):
                        _id = _.get('ai_id', None)

                        if _id and _id not in data:
                            data[_id] = _

        return sorted(data.values(), key=lambda x: x.get('published_on', None), reverse=True)

    def import_content(self):

        try:
            context = self.site.restrictedTraverse('research/publications')
        except:
            self.log(u"No research publications page found.")
        else:
            publications = self.publications

            v = BaseView(self.context, self.request)

            html = v.publications_html(publications=publications[0:500])

            context.text = RichTextValue(
                raw=html,
                mimeType=u'text/html',
                outputMimeType='text/x-html-safe'
            )

            context.reindexObject()

            transaction.commit()