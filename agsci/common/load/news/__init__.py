from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bs4 import BeautifulSoup
from calendar import timegm
from datetime import datetime
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import feedparser
import json
import re
import requests
import time

from agsci.common.constants import DEFAULT_TIMEZONE, AGSCI_DOMAIN
from agsci.common.utilities import localize, ploneify, getDepartmentId

from .. import ImportContentView

class ImportNewsView(ImportContentView):

    _initial_date = '2021-10-27'

    @property
    def initial_date(self):
        return localize(datetime.strptime(self._initial_date, '%Y-%m-%d'))

    url = 'https://www.psu.edu/news/rss/agricultural-sciences/rss.xml'

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"

    # Transform from news tag to Plone tag
    tag_transforms = {
        'agribusiness-management-major' : 'majors-agribusiness-management',
        'agricultural-and-extension-education-major' : 'majors-agricultural-and-extension-education',
        'agricultural-science-major' : 'majors-agricultural-science',
        'animal-science-major' : 'majors-animal-science',
        'biological-engineering-major' : 'majors-biological-engineering',
        'biorenewable-systems-major' : 'majors-biorenewable-systems',
        'community-environment-and-development-major' : 'majors-community-environment-and-development',
        'environmental-resource-management-major' : 'majors-environmental-resource-management',
        'food-science-major' : 'majors-food-science',
        'forest-ecosystem-management-major' : 'majors-forest-ecosystem-management',
        'immunology-and-infectious-disease-major' : 'majors-immunology-and-infectious-disease',
        'landscape-contracting-major' : 'majors-landscape-contracting',
        'plant-sciences-major' : 'majors-plant-sciences',
        'toxicology-major' : 'majors-toxicology',
        'turfgrass-science-major' : 'majors-turfgrass-science',
        'veterinary-and-biomedical-sciences-major' : 'majors-veterinary-and-biomedical-sciences',
        'wildlife-and-fisheries-science-major' : 'majors-wildlife-and-fisheries-science',
        'department-of-agricultural-and-biological-engineering' : 'department-agricultural-and-biological-engineering',
        'department-of-agricultural-economics-sociology-and-education' : 'department-agricultural-economics-sociology-and-education',
        'department-of-animal-science' : 'department-animal-science',
        'department-of-ecosystem-science-and-management' : 'department-ecosystem-science-and-management',
        'department-of-entomology' : 'department-entomology',
        'department-of-food-science' : 'department-food-science',
        'department-of-plant-pathology-and-environmental-microbiology' : 'department-plant-pathology-and-environmental-microbiology',
        'department-of-plant-science' : 'department-plant-science',
        'department-of-plant-sciences' : 'department-plant-science',
        'department-of-veterinary-and-biomedical-sciences' : 'department-veterinary-and-biomedical-sciences',
        'penn-state-master-gardeners' : 'master-gardeners',
        'penn-state-extension' : 'extension',
        'student-stories' : 'students',
    }

    conditional_transforms = {
        ('student-stories', 'students') : {
            'agribusiness-management' : 'majors-agribusiness-management',
            'agricultural-and-extension-education' : 'majors-agricultural-and-extension-education',
            'agricultural-science' : 'majors-agricultural-science',
            'animal-science' : 'majors-animal-science',
            'biological-engineering' : 'majors-biological-engineering',
            'biorenewable-systems' : 'majors-biorenewable-systems',
            'community-environment-and-development' : 'majors-community-environment-and-development',
            'environmental-resource-management' : 'majors-environmental-resource-management',
            'food-science' : 'majors-food-science',
            'forest-ecosystem-management' : 'majors-forest-ecosystem-management',
            'immunology-and-infectious-disease' : 'majors-immunology-and-infectious-disease',
            'landscape-contracting' : 'majors-landscape-contracting',
            'plant-sciences' : 'majors-plant-sciences',
            'toxicology' : 'majors-toxicology',
            'turfgrass-science' : 'majors-turfgrass-science',
            'veterinary-and-biomedical-sciences' : 'majors-veterinary-and-biomedical-sciences',
            'wildlife-and-fisheries-science' : 'majors-wildlife-and-fisheries-science',
        }
    }

    department_tag_config = {
        "abe": [
            "department-agricultural-and-biological-engineering",
            "majors-biological-engineering",
            "majors-biorenewable-systems",
        ],
        "aese": [
            "department-agricultural-economics-sociology-and-education",
            "majors-agribusiness-management",
            "majors-agricultural-and-extension-education",
            "majors-agricultural-science",
            "majors-community-environment-and-development",
        ],
        "animalscience": [
            "department-animal-science",
            "majors-animal-science",
        ],
        "ecosystems": [
            "department-ecosystem-science-and-management",
            "majors-forest-ecosystem-management",
            "majors-environmental-resource-management",
            "majors-wildlife-and-fisheries-science",
        ],
        "ento": [
            "department-entomology",
        ],
        "foodscience": [
            "department-food-science",
            "majors-food-science",
        ],
        "plantpath": [
            "department-plant-pathology-and-environmental-microbiology",
            "majors-plant-sciences",
        ],
        "plantscience": [
            "department-plant-science",
            "majors-landscape-contracting",
            "majors-plant-sciences",
            "majors-turfgrass-science",
        ],
        "vbs": [
            "department-veterinary-and-biomedical-sciences",
            "majors-immunology-and-infectious-disease",
            "majors-toxicology",
            "majors-veterinary-and-biomedical-sciences",
        ],
        'agsci/apd/news' : [
            "news-ag-progress-days",
        ],
    }

    def transform_tag(self, _, tags=[]):
        _ = self.tag_transforms.get(_, _)

        for (k, v) in self.conditional_transforms.items():

            if any([x in tags for x in k]):
                _ = v.get(_, _)

        return _

    @property
    def valid_tags(self):

        # Tags (excluding news-)
        tags = [
            'research',
            'student-stories',
            'students',
            'international',
            'extension',
            'pennsylvania-4-h',
            'master-gardeners',
            'ag-progress-days',
        ]

        # Include the "to" values from tag_transform
        tags.extend(self.tag_transforms.values())

        # Unique values to prevent duplicates
        return list(set(tags))

    @property
    def department_id(self):
        return getDepartmentId()

    @property
    def department_tags(self):
        return self.department_tag_config.get(self.department_id, [])

    def create_news_item(self, **kwargs):

        item = createContentInContainer(
            self.context,
            "News Item",
            id=kwargs['id'],
            title=kwargs['title'],
            description=kwargs['description'],
            article_link=kwargs['url'],
            exclude_from_nav=True,
            checkConstraints=False
        )

        # Set image
        image = kwargs['image']

        if image:
            item.image = image

        # Grab article image and set it as contentleadimage
        html = self.get_html(kwargs['url'])

        if html:

            item.text = RichTextValue(
                raw=self.getBodyText(html),
                mimeType=u'text/html',
                outputMimeType='text/x-html-safe'
            )

        dateStamp = DateTime(kwargs['date'])

        item.setModificationDate(dateStamp)
        item.setEffectiveDate(dateStamp)

        tags = self.get_tags(html)

        if tags:

            item.setSubject(tags)

        # Publish
        if self.wftool.getInfoFor(item, 'review_state').lower() != 'published':
            self.wftool.doActionFor(item, 'publish')

        item.reindexObject()

        return item

    def get_entry_date(self, _):

        date_published_parsed = _.get('published_parsed')
        updated_parsed = _.get('updated_parsed')
        effective = _.get('effective', None)

        fmt = '%%Y-%%m-%%d %%H:%%M %s' % DEFAULT_TIMEZONE

        now = datetime.now()
        dateStamp = now.strftime(fmt)

        if effective:
            dateStamp = effective

        elif date_published_parsed:

            local_time = time.localtime(timegm(date_published_parsed))
            dateStamp = time.strftime(fmt, local_time)

        elif updated_parsed and isinstance(updated_parsed, time.struct_time):

            dateStamp = time.strftime(fmt, updated_parsed)

        return localize(DateTime(dateStamp))

    @property
    def news_items(self):
        numeric_ids = [x for x in self.portal_catalog.uniqueValuesFor('id') if x.isdigit() or x[:8].isdigit()]

        return self.portal_catalog.searchResults({
            'portal_type' : 'News Item',
            'id' : numeric_ids,
            'path' : '/'.join(self.context.getPhysicalPath()),
            'created' : {
                'range' : 'min',
                'query' : DateTime() - 365,
            }
        })

    @property
    def department_news_feed(self):

        data = []

        url = "https://%s/@@tagged-news-feed" % AGSCI_DOMAIN

        department_tags = self.department_tags

        if department_tags:

            response = requests.get(
                url,
                headers={
                    'User-Agent': self.user_agent
                },
                verify=False
            )

            if response.status_code == 200:

                for _ in response.json():

                    subject = _.get('Subject', [])

                    if subject and any([x in subject for x in department_tags]):
                        data.append(_)

        return data

    @property
    def news_feed(self):
        feed = feedparser.parse(self.url)
        return feed['entries']

    @property
    def feed(self):

        if self.department_id:

            return self.department_news_feed

        return self.news_feed

    def get_item_id(self, item):
        _date = self.get_entry_date(item)
        _title = item.get('title', '')

        if _date and _title:
            _datestamp = _date.strftime('%Y%m%d')
            return '%s-%s' % (_datestamp, ploneify(_title))

    def import_content(self):

        rv = ["Syncing RSS feeds from %s" % self.url]

        news_ids = [x.getId for x in self.news_items]

        for item in self.feed:

            # Only import items after hardcoded date
            _date = self.get_entry_date(item)

            if _date < self.initial_date:
                continue

            _id = self.get_item_id(item)

            if _id and _id not in news_ids:

                _link = item.get('link', '')
                _title = item.get('title', None)
                _description = item.get('summary_detail', {}).get('value')

                # Convert HTML description to plain text
                if _description and '<' in _description:
                    _description = BeautifulSoup(_description, features="lxml").text

                # Get Image URL
                image = self.get_image(item)

                item = self.create_news_item(
                    id=_id,
                    title=_title,
                    description=_description,
                    url=_link,
                    date=_date,
                    image=image,
                )

                rv.append("Created %s" % _id)

            else:
                rv.append("Skipped %s" % _id)

        return json.dumps(rv, indent=4)

    def getBodyText(self, html):
        soup = BeautifulSoup(html, features='lxml')

        try:
            item = soup.find("div", {'id' : re.compile('text-content-container')})
        except:
            return "<p></p>"

        return u"<p>%s</p>" % safe_unicode(item.text)

    def get_tags(self, html, raw=False, valid=True):
        soup = BeautifulSoup(html, features='lxml')

        tags = []

        for tags_div in soup.findAll("ul", {'class' : re.compile('^article-tags_list')}):
            items = tags_div.findAll("li")
            tags.extend([ploneify(x.text).strip() for x in items])

        # Transform tags
        if not raw:
            tags = [self.transform_tag(x, tags) for x in tags]

        # Ensure valid
        if valid:
            tags = list(set(tags) & set(self.valid_tags))

        # Prepend 'news-' to tags if they don't start with 'majors-' or 'department-'
        if not raw:
            for i in range(0, len(tags)):
                t = tags[i]
                if not any([t.startswith('%s-' % x) for x in ('majors', 'department')]):
                    t = 'news-%s' % t
                    tags[i] = t

        return tags

    @property
    def portal_transforms(self):
        return getToolByName(self.context, 'portal_transforms')

    def get_html(self, url):
        response = requests.get(url, headers={ 'User-Agent': self.user_agent })

        if response.status_code == 200:
            return response.text

    def get_image(self, item):

        image_url = None

        if 'has_lead_image' in item:
            if item['has_lead_image']:
                image_url = 'https://%s%s/@@images/image' % (AGSCI_DOMAIN, item.get('path'))
        else:
            links = item.get('links', [])
            image_links = [x.get('href', '') for x in links if x.get('rel', None) in ('enclosure',)]

            if image_links:
                image_url = image_links[0]

        if image_url:
            image_data = self.download_image(image_url)

            filename = image_url.split('/')[-1].split('?')[0]

            if filename:
                filename = safe_unicode(filename)
            else:
                filename = u'image'

            if image_data:
                return NamedBlobImage(
                    filename=filename,
                    data=image_data
                )

    def download_image(self, url):
        response = requests.get(url, headers={ 'User-Agent': self.user_agent }, stream=True, verify=False)

        if response.status_code == 200:
            response.raw.decode_content = True
            return response.raw.read()

# Blog-specific view
class ImportNewsBlogView(ImportNewsView):

    @property
    def department_id(self):
        site_id = self.site.getId().replace('.psu.edu', '')
        path = self.context.absolute_url()[len(self.site.absolute_url()):]
        return '%s%s' % (site_id, path)

