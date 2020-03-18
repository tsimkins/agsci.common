from DateTime import DateTime
from bs4 import BeautifulSoup
from plone.app.textfield.value import RichTextValue

import requests

from .. import ImportContentView

class ImportFacultyPublicationsView(ImportContentView):

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

    def _get_publications(self, user_id):

        pubs_api_url = "/v1/users/%s/publications"
        publications = self.get_api_data(pubs_api_url, user_id, format='html')
        soup = BeautifulSoup(publications, features="lxml")
        soup.html.hidden = True
        soup.body.hidden = True
        return unicode(soup.find('ul'))

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
            username = getattr(o, 'username', None)

            if username:
                try:
                    data = self.get_publications(username)
                except:
                    pass
                else:
                    if data:
                        html = "".join([u"<p>%s</p>" % x for x in data[:25]])
                        o.publications = RichTextValue(
                            raw=html,
                            mimeType=u'text/html',
                            outputMimeType='text/x-html-safe'
                        )

    @property
    def department_publications(self):
        faculty_ids = [x.getId for x in self.faculty]

        api_url = '/v1/users/publications?order_first_by=publication_date_desc&order_second_by=title_asc'

        return self.get_api_data(
            api_url,
            method='post',
            body=faculty_ids
        )