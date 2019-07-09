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
from urlparse import urljoin
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

import feedparser
import re
import requests
import time
import urllib2

from agsci.common.constants import DEFAULT_TIMEZONE
from agsci.common.utilities import localize

class ImportNewsView(BrowserView):

    url = 'http://news.psu.edu/rss/college/agricultural-sciences'

    user_agent = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0"

    IMAGE_FIELD_NAME = 'image'
    IMAGE_CAPTION_FIELD_NAME = 'imageCaption'

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
    }

    def transform_tag(self, _):
        return self.tag_transforms.get(_, _)

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
        html = self.getHTML(kwargs['url'])

        if html:

            item.text = RichTextValue(
                raw=self.getBodyText(html),
                mimeType=u'text/html',
                outputMimeType='text/x-html-safe'
            )

            # Set Lead Image or Image field
            (image, image_caption) = self.getImageAndCaption(html)

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

        tags = self.getTags(html)

        if tags:

            # Prepend 'news-' to tags if they don't start with 'majors-' or 'department-'
            for i in range(0, len(tags)):
                t = tags[i]
                if not any([t.startswith('%s-' % x) for x in ('majors', 'department')]):
                    t = 'news-%s' % t
                    tags[i] = t

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

    def __call__(self):

        alsoProvides(self.request, IDisableCSRFProtection)

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

    def getTags(self, html):
        valid_tags = self.valid_tags

        soup = BeautifulSoup(html, features='lxml')

        try:
            article_tags = []

            for tags_div in soup.findAll("div", {'class' : re.compile('article-related-terms')}):
                items = tags_div.findAll("a")
                article_tags.extend([ploneify(x.contents[0].text).strip() for x in items])

            # Transform tags
            article_tags = [self.transform_tag(x) for x in article_tags]

            if valid_tags:
                tags = list(set(valid_tags) & set(article_tags))
            else:
                tags = list(article_tags)

            return tags

        except:
            return []

    @property
    def portal_transforms(self):
        return getToolByName(self.context, 'portal_transforms')

    def getHTML(self, url):
        response = requests.get(url, headers={ 'User-Agent': self.user_agent })

        if response.status_code == 200:
            return response.text

    def getImageAndCaption(self, html=None, url=None):

        if not (html or url):
            return (None, None)
        elif not html:
            html = self.getHTML(url)

        soup = BeautifulSoup(html, features='lxml')

        img_url = ""
        img_caption = ""
        imgSrc = ""

        # Remove related nodes
        for _ in soup.findAll("div", {'class' : 'related-nodes'}):
            __ = _.extract()

        for div in soup.findAll("div", attrs={'class' : re.compile('image')}):
            for img in div.findAll("img"):
                img_url = img.get('src')
                if img_url:
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
            if img_url:
                break

        if not img_url:
            img_caption = ""
            for ul in soup.findAll("ul", {'class' : 'slides'}):
                for li in ul.findAll('li'):
                    try:
                        img_url = li.find("div", {'class' : re.compile('field-name-field-image')}).find("img").get('src')
                        img_caption = li.find("div", {'class' : re.compile('field-name-field-flickr-description')}).text
                    except:
                        pass
                    if img_url:
                        break
        if img_url:
            imgSrc = urljoin(url, img_url)

        if imgSrc:
            imgData = self.download_image(imgSrc)

            filename = img_url.split('/')[-1].split('?')[0]

            if filename:
                filename = safe_unicode(filename)
            else:
                filename = u'image'

            image_field = NamedBlobImage(
                filename=filename,
                data=imgData
            )

            return (image_field, img_caption)

        else:
            return (None, None)

    def hasImage(self, context):
        image_field = context.getField(IMAGE_FIELD_NAME).get(context)

        if image_field and image_field.size:
            return True
        else:
            return False

    def download_image(self, url):
        response = requests.get(url, headers={ 'User-Agent': self.user_agent }, stream=True)

        if response.status_code == 200:
            response.raw.decode_content = True
            return response.raw.read()

    def setImage(self, item, image_url=None, html=None):
        # Given an article, and either an image URL or a set of HTML, sets the image
        # and caption for the article.

        theImage = theImageCaption = ""

        if image_url:
            theImage = self.download_image(image_url)
            theImageCaption = ""
        else:
            if not html:
                if hasattr(item, 'getRemoteUrl'):
                    url = item.getRemoteUrl()
                elif hasattr(item, 'article_link'):
                    url = item.article_link
                else:
                    url = None

                if url:
                    html = self.getHTML(url)
                else:
                    return None

            # Grab article image and caption
            (theImage, theImageCaption) = getImageAndCaption(html=html)

        if theImage:
            item.getField(IMAGE_FIELD_NAME).set(item, theImage)
            item.getField(IMAGE_CAPTION_FIELD_NAME).set(item, theImageCaption)
            item.reindexObject()
            print "setImage for %s" % item.id
        else:
            print "No Image for %s" % item.id


    def retroSetImages(self):
        for item in self.context.listFolderContents(contentFilter={"portal_type" : "News Item"}):

            self.setImage(item)

    data = {
        'extension': ['cooperative-extension', 'penn-state-cooperative-extension', 'extension', 'penn-state-extension'],
        'aec' : ['earth-and-environment', 'chesapeake-bay', 'energy', 'water', 'water-quality', 'environmental-engineering', 'environment', 'environmental-stewardship', 'forestry']
    }


    def setTags(context, tag):
        # Tag Feeds

        print "Settings %s within %s" % (tag, context.absolute_url())

        if tag not in data.keys():
            return False
        else:
            urls = data[tag]

        print "Urls to search: %s" % ", ".join(urls)

        linkRegex = re.compile("<link>http://news.psu.edu/story/(\d+)/.*?</link>", re.I|re.M)

        found_articles = False

        for u in urls:
            print "Sleeping 10"
            time.sleep(10)
            tag_url = 'http://news.psu.edu/rss/tag/%s' % u
            print "Grabbing %s" % tag_url
            rss = urllib2.urlopen(tag_url).read()
            for m in re.finditer(linkRegex, rss):
                link = m.group(1)
                if link in context.objectIds():
                    story = context[link]
                    subject = list(story.Subject())
                    if not subject.count('news-%s' % tag):
                        subject.append('news-%s' % tag)
                        print "New subject for %s : %s" % (link, str(subject))
                        found_articles = True
                        story.setSubject(tuple(subject))
                        story.reindexObject()

        return found_articles

