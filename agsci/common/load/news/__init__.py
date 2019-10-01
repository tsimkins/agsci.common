from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from bs4 import BeautifulSoup
from calendar import timegm
from datetime import datetime
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage
from urllib2 import HTTPError
from zope.component import getUtility
from zope.component.hooks import getSite

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import feedparser
import re
import requests
import time
import urllib2

from agsci.common.constants import DEFAULT_TIMEZONE
from agsci.common.utilities import localize, ploneify

from .. import ImportContentView

class ImportNewsView(ImportContentView):

    url = 'http://news.psu.edu/rss/college/agricultural-sciences'

    user_agent = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0"

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


    def transform_tag(self, _, tags=[]):
        _ = self.tag_transforms.get(_, _)

        for (k, v) in self.conditional_transforms.iteritems():

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
        ]

        # Include the "to" values from tag_transform
        tags.extend(self.tag_transforms.values())

        # Unique values to prevent duplicates
        return list(set(tags))

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

        # Grab article image and set it as contentleadimage
        html = self.get_html(kwargs['url'])

        if html:

            item.text = RichTextValue(
                raw=self.getBodyText(html),
                mimeType=u'text/html',
                outputMimeType='text/x-html-safe'
            )

            # Set Lead Image or Image field
            (image, image_caption) = self.get_image_and_caption(html)

            if image:
                item.image = image

                # Unset full width field if image is too small, or is portrait.
                try:
                    (w,h) = image.getImageSize()
                except:
                    pass
                else:
                    if w < h or w < 600:
                        item.image_full_width = False

                if image_caption:
                    item.image_caption = image_caption


        dateStamp = DateTime(kwargs['date'])

        item.setModificationDate(dateStamp)
        item.setEffectiveDate(dateStamp)

        tags = self.get_tags(html)

        if tags:

            item.setSubject(tags)

        # Publish
        if self.wftool.getInfoFor(item, 'review_state') != 'Published':
            self.wftool.doActionFor(item, 'publish')

        item.reindexObject()

        return item

    def get_entry_date(self, _):

        date_published_parsed = _.get('published_parsed')
        updated_parsed = _.get('updated_parsed')

        fmt = '%%Y-%%m-%%d %%H:%%M %s' % DEFAULT_TIMEZONE

        now = datetime.now()
        dateStamp = now.strftime(fmt)

        if date_published_parsed:

            local_time = time.localtime(timegm(date_published_parsed))
            dateStamp = time.strftime(fmt, local_time)

        elif updated_parsed and isinstance(updated_parsed, time.struct_time):

            dateStamp = time.strftime(fmt, updated_parsed)

        return localize(DateTime(dateStamp))

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def wftool(self):
        return getToolByName(self.context, 'portal_workflow')

    def import_content(self):

        rv = ["Syncing RSS feeds from %s" % self.url]

        numeric_ids = [x for x in self.portal_catalog.uniqueValuesFor('id') if x.isdigit()]

        news_ids = [x.getId for x in self.portal_catalog.searchResults({'portal_type' : 'News Item', 'id' : numeric_ids, 'SearchText' : 'news.psu.edu'})]

        feed = feedparser.parse(self.url)

        for item in feed['entries']:

            _link = item.get('link', '')
            _id = str(_link.split("/")[4]).split('#')[0]

            if _id not in news_ids:

                _title = item.get('title', None)
                _description = item.get('summary_detail', {}).get('value')

                item = self.create_news_item(
                    id=_id,
                    title=_title,
                    description=_description,
                    url=_link,
                    date=self.get_entry_date(item)
                )

                rv.append("Created %s" % _id)

            else:
                rv.append("Skipped %s" % _id)

        return rv

    def getBodyText(self, html):
        soup = BeautifulSoup(html, features='lxml')

        try:
            body = soup.find("div", {'class' : re.compile('field-name-body')})
            item = body.find("div", {'class' : re.compile('field-item($|\s+)')})
        except:
            return ""

        return u"<p>%s</p>" % safe_unicode(item.text)

    def get_tags(self, html, raw=False, valid=True):
        soup = BeautifulSoup(html, features='lxml')

        tags = []

        for tags_div in soup.findAll("div", {'class' : re.compile('article-related-terms')}):
            items = tags_div.findAll("a")
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

    def get_image_and_caption(self, html=None, url=None):

        if not (html or url):
            return (None, None)
        elif not html:
            html = self.get_html(url)

        soup = BeautifulSoup(html, features='lxml')

        image_url = ""
        img_caption = ""
        image_src = ""

        # Remove related nodes
        for _ in soup.findAll("div", {'class' : 'related-nodes'}):
            __ = _.extract()

        for div in soup.findAll("div", attrs={'class' : re.compile('image')}):

            for img in div.findAll("img"):

                image_url = img.get('src')

                if image_url:

                    parent = div.parent

                    for caption in parent.findAll("div", attrs={'class' : re.compile('short-caption')}):
                        img_caption = caption.text

                        if img_caption:
                            break

                    if not img_caption:

                        for span in div.findAll("span", {'property' : 'dc:title'}):

                            img_caption = span.get('content')

                            if img_caption:
                                break

            if image_url:
                break

        if not image_url:

            img_caption = ""

            for ul in soup.findAll("ul", {'class' : 'slides'}):

                for li in ul.findAll('li'):

                    try:
                        image_url = li.find("div", {'class' : re.compile('field-name-field-image')}).find("img").get('src')
                        img_caption = li.find("div", {'class' : re.compile('field-name-field-flickr-description')}).text
                    except:
                        pass

                    if image_url:
                        break

        if image_url:
            image_src = urljoin(url, image_url)

            if image_src:
                image_data = self.download_image(image_src)

                filename = image_url.split('/')[-1].split('?')[0]

                if filename:
                    filename = safe_unicode(filename)
                else:
                    filename = u'image'

                image_field = NamedBlobImage(
                    filename=filename,
                    data=image_data
                )

                return (image_field, img_caption)

        else:
            return (None, None)

    def download_image(self, url):
        response = requests.get(url, headers={ 'User-Agent': self.user_agent }, stream=True)

        if response.status_code == 200:
            response.raw.decode_content = True
            return response.raw.read()
