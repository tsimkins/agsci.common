from Acquisition import aq_chain, aq_base
from bs4 import BeautifulSoup, Tag, NavigableString
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from datetime import datetime, timedelta
from plone.registry.interfaces import IRegistry
from urlparse import urlparse
from zope.annotation.interfaces import IAnnotations
from zope.component import subscribers, getAdapters, getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import Interface

from agsci.common.constants import DEFAULT_TIMEZONE
from agsci.common.decorators import context_memoize
from agsci.common.utilities import ploneify, truncate_text, localize

from .error import ContentCheckError, ManualCheckError
from ..behaviors.leadimage import LeadImage

import pytz
import re
import requests

alphanumeric_re = re.compile("[^A-Za-z0-9]+", re.I|re.M)

# Cached version of _getIgnoreChecks
def getIgnoreChecks(context):

    request = getRequest()

    key = "ignore-checks-%s" % context.UID()

    cache = IAnnotations(request)

    data = cache.get(key, None)

    if not isinstance(data, list):
        data = _getIgnoreChecks(context)
        cache[key] = data

    return data

def _getIgnoreChecks(context):

    for o in context.aq_chain:

        if IPloneSiteRoot.providedBy(o):
            break

        ignore_checks = getattr(o.aq_base, 'ignore_checks', [])

        if ignore_checks:
            return ignore_checks

    return []

# Cache errors on HTTP Request, since we may be calling this multiple times.
# Ref: http://docs.plone.org/manage/deploying/performance/decorators.html#id7
def getValidationErrors(context):

    request = getRequest()

    key = "validation-errors-%s" % context.UID()

    cache = IAnnotations(request)

    data = cache.get(key, None)

    if not isinstance(data, list):
        data = _getValidationErrors(context)
        cache[key] = data

    return data

def _getValidationErrors(context):

    errors = []

    ignore_checks = getIgnoreChecks(context)

    for i in subscribers((context,), IContentCheck):

        if i.error_code not in ignore_checks:

            try:
                for j in i:
                    errors.append(j)

            except Exception as e:
                errors.append(
                    ContentCheckError(i, u"Internal error running check: '%s: %s'" % (e.__class__.__name__, e.message))
                )

    # Sort first on the hardcoded order
    errors.sort(key=lambda x: x.sort_order)

    return errors


# Interface for warning subscribers
class IContentCheck(Interface):
    pass


# Base class for content check
class ContentCheck(object):

    # Title for the check
    title = "Default Check"

    # Description for the check
    description = ""

    # Action to remediate the issue
    action =""

    # Render the output as HTML.
    render = False

    # Render the action output as HTML
    render_action = False

    # Sort order (lower is higher)
    sort_order = 0

    # Timeout for cache
    CACHED_DATA_TIMEOUT = 600 # Ten minutes

    def __init__(self, context):
        self.context = context

    @property
    def registry(self):
        return getUtility(IRegistry)

    @property
    def error_code(self):
        return self.__class__.__name__

    @property
    def request(self):
        return getRequest()

    def value(self):
        """ Returns the value of the attribute being checked """

    def check(self):
        """ Performs the check and returns ContentCheckError/ContentCheckError/ContentCheckError/None """

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def wftool(self):
        return getToolByName(self.context, 'portal_workflow')

    @property
    def portal_transforms(self):
        return getToolByName(self.context, 'portal_transforms')

    @property
    def review_state(self):
        return self.wftool.getInfoFor(self.context, 'review_state')

    def __iter__(self):
        return self.check()

    # Returns an object with the keyword arguments as properties
    def object_factory(self, **kwargs):
        from agsci.common import object_factory as _
        return _(**kwargs)

    @property
    def now(self):
        return datetime.now(pytz.timezone(DEFAULT_TIMEZONE))

# Validates the title length
class TitleLength(ContentCheck):

    title = "Title Length"
    description = "Titles should be no more than 60 characters."
    action = "Edit the title to be no more than 60 characters.  For short titles, add more detail."

    # Sort order (lower is higher)
    sort_order = 1

    def value(self):
        return len(self.context.title)

    def check(self):
        v = self.value()

        if v > 60:
            yield ContentCheckError(self, u"%d characters is too long." % v)
        elif v < 3:
            yield ContentCheckError(self, u"%d characters may be too short." % v)


# Validates the description length
class DescriptionLength(ContentCheck):

    limit = 300

    title = "Description Length"
    description = "Content must have a description, which should be a maximum of %d characters." % limit
    action = "Edit the description to be no more than %d characters.  For short or missing descriptions, add more detail." % limit

    # Sort order (lower is higher)
    sort_order = 1

    def value(self):
        if hasattr(self.context, 'description'):
            if isinstance(self.context.description, (str, unicode)):
                return len(self.context.description)

        return 0

    def check(self):

        v = self.value()

        if v > self.limit:
            yield ContentCheckError(self, u"%d characters is too long." % v)
        elif v == 0:
            yield ContentCheckError(self, u"A description is required for this content.")
        elif v < 32:
            yield ContentCheckError(self, u"%d characters may be too short." % v)

# Checks for issues in the text.  This doesn't actually check, but is a parent
# class for other checks.
class BodyTextCheck(ContentCheck):

    # Title for the check
    title = "HTML: Body Text Check"

    # Description for the check
    description = ""

    # Sort order (lower is higher)
    sort_order = 10

    # h1 - h6
    all_heading_tags = ['h%d' % x for x in range(1,7)]

    resolveuid_re = re.compile("resolveuid/([abcdef0-9]{32})", re.I|re.M)

    @property
    def internal_link_uids(self):

        _ = []

        for a in self.getLinks():

            href = a.get('href', '')

            if href:

                m = self.resolveuid_re.match(href)

                if m:
                    _.append(m.group(1))
        return _

    @property
    def internal_image_uids(self):

        _ = []

        for a in self.getImages():

            href = a.get('src', '')

            if href:

                m = self.resolveuid_re.match(href)

                if m:
                    _.append(m.group(1))
        return _

    def getHTML(self, o):

        if hasattr(o, 'aq_base'):
            _o = o.aq_base

            if hasattr(_o, 'text') and hasattr(_o.text, 'raw'):
                if _o.text.raw:
                    return safe_unicode(_o.text.raw)

        return ''

    def html_to_text(self, html):
        text = self.portal_transforms.convert('html_to_text', html).getData()
        text = " ".join(text.strip().split())
        return safe_unicode(text)

    def soup_to_text(self, soup):
        html = safe_unicode(repr(soup))
        text = self.portal_transforms.convert('html_to_text', html).getData()
        text = " ".join(text.strip().split())
        return safe_unicode(text)

    def value(self):
        return self.html

    @property
    @context_memoize
    def soup(self):
        return BeautifulSoup(self.html, features='lxml')

    @property
    @context_memoize
    def html(self):
        return safe_unicode(self.getHTML(self.context))

    @property
    @context_memoize
    def text(self):
        return self.html_to_text(self.html)

    def toWords(self, text):
        text = text.lower()
        text = text.replace('@psu.edu', '__PENN_STATE_EMAIL_ADDRESS_DOMAIN__')
        text = alphanumeric_re.sub(' ', text).split()
        return list(set(text))

    @property
    def words(self):
        return self.toWords(self.text)

    def check(self):
        pass

    def getLinks(self):
        return self.soup.findAll('a')

    def getImages(self):
        return self.soup.findAll('img')

    def getHeadings(self):
        return self.soup.findAll(self.all_heading_tags)

    @property
    @context_memoize
    def uid_to_brain(self):
        return dict([(x.UID, x) for x in self.portal_catalog.searchResults()])


# Checks for appropriate heading level hierarchy, e.g. h2 -> h3 -> h4
class BodyHeadingCheck(BodyTextCheck):

    def value(self):
        return self.getHeadings()

# Generic Image check that returns all <img> tags as the value()
class BodyImageCheck(BodyTextCheck):

    def value(self):
        return self.soup.findAll('img')


# Generic Image check that returns all <img> tags as the value()
class BodyLinkCheck(BodyTextCheck):

    bad_domains = []
    ok_urls = []

    def parse_url(self, url, strip_slash=False):
        parsed_url = urlparse(url)

        domain = parsed_url.netloc
        path = parsed_url.path
        scheme = parsed_url.scheme

        if strip_slash:
            if path.endswith('/'):
                path = path[:-1]

        return (scheme, domain, path)

    def url_equivalent(self, url_1, url_2, match_protocol=True):

        (scheme_1, domain_1, path_1) = self.parse_url(url_1, strip_slash=True)
        (scheme_2, domain_2, path_2) = self.parse_url(url_2, strip_slash=True)

        (_scheme, _domain, _path) = (
            scheme_1==scheme_2,
            domain_1==domain_2,
            path_1==path_2,
        )

        if match_protocol:
            return _scheme and _domain and _path

        return _domain and _path

    def value(self):
        return self.soup.findAll('a')

    def is_bad_url(self, url):

        if url:

            (scheme, domain, path) = self.parse_url(url)

            # Handle no-domain cases
            if not domain:

                # Mailto is fine
                if scheme == 'mailto':
                    return False

                # URLs with 'resolveuid' are OK
                if path.startswith('resolveuid'):
                    return False

                # Otherwise, URLs should have a domain
                return True

            # Check for 'bad' domains
            elif domain in self.bad_domains:

                # If our domain/path is in the `ok_urls` list, it's an exception.
                for (_d, _p) in self.ok_urls:

                    if domain == _d and path.startswith(_p):
                        return False

                return True

# Checks for appropriate heading level hierarchy, e.g. h2 -> h3 -> h4
class HeadingLevels(BodyHeadingCheck):

    # Title for the check
    title = "HTML: Heading Levels"

    # Description for the check
    description = "Validates that the heading level hierarchy is correct."

    # Remedial Action
    action = "In the text, validate that the heading levels are in the correct order, and none are skipped."

    def check(self):

        headings = self.value()

        # Get heading tag object names (e.g. 'h2')
        heading_tags = [x.name for x in headings]

        # If no heading tags to check, return
        if not heading_tags:
            return

        # Check if we have an h1 (not permitted)
        if 'h1' in heading_tags:
            yield ContentCheckError(self, "An <h1> heading is not permitted in the body text.")

        # Validate that the first tag in the listing is an h2
        if heading_tags[0] != 'h2':
            yield ContentCheckError(self, "The first heading in the body text must be an <h2>.")

        # Check for heading tag order, and ensure we don't skip any
        for i in range(0, len(heading_tags)-1):
            this_heading = heading_tags[i]
            next_heading = heading_tags[i+1]

            this_heading_idx = self.all_heading_tags.index(this_heading)
            next_heading_idx = self.all_heading_tags.index(next_heading)

            if next_heading_idx > this_heading_idx and next_heading_idx != this_heading_idx + 1:
                heading_tag_string = "<%s> to <%s>" % (this_heading, next_heading) # For error message
                yield ContentCheckError(self, "Heading levels in the body text are skipped or out of order: %s" % heading_tag_string)


# Check for heading length
class HeadingLength(BodyHeadingCheck):

    # Title for the check
    title = "HTML: Heading Text Length"

    # Description for the check
    description = "Validates that the heading text is not too long. "

    # Remedial Action
    action = "Ensure that headings are a maximum of 120 characters, and ideally 60 characters or less."

    # Warning levels for h2 and h3.  Allow h3's to be slightly longer before a warning is triggered.
    warning_levels = {
                        'h2' : 60,
                        'h3' : 100,
    }

    def check(self):
        headings = self.getHeadings()

        for i in headings:
            text = self.soup_to_text(i)
            warning_length = self.warning_levels.get(i.name, 99999)

            v = len(text)

            if v > 200:
                yield ContentCheckError(self, u"Length of %d characters for <%s> heading '%s' is too long." % (v, i.name, text))

# Prohibited words and phrases. Checks for individual words, phrases, and regex patterns in body text.
class ProhibitedWords(BodyTextCheck):

    title = "HTML: Words/phrases to avoid."

    description = "In order to follow style or editoral standards, some words (e.g. 'PSU') should not be used."

    action = "Replace the words/phrases identified with appropriate alternatives."

    # List of individual words (alphanumeric only, will be compared case-insenstive.)
    find_words = ['PSU',]

    # List of phrases, will be checked for 'in' body text.
    find_phrases = ['Agronomy Facts',]

    # Regex patterns.  These are probably 'spensive.
    find_patterns = ['https*://',]

    def check(self):

        # Get a list of individual
        words = self.words
        text = self.text.lower()

        for i in self.find_words:
            if i.lower() in words:
                yield ContentCheckError(self, 'Found word "%s" in body text.' % i)

        for i in self.find_phrases:
            if i.lower() in text:
                yield ContentCheckError(self, 'Found phrase "%s" in body text.' % i)

        for i in self.find_patterns:
            i_re = re.compile('(%s)' %i, re.I|re.M)
            _m = i_re.search(text)

            if _m:
                yield ContentCheckError(self, 'Found "%s" in body text.' % _m.group(0))


# Verifies that a lead image is assigned to the content
class HasLeadImage(ContentCheck):

    title = "Lead Image"

    description = "A quality lead image is suggested to provide a visual connection for the user, and to display in search results."

    action = "Please add a quality lead image to this content."

    # Sort order (lower is higher)
    sort_order = 5

    # Has lead image?
    @property
    def has_image(self):
        return LeadImage(self.context).has_image

    @property
    def image_format(self):
        return LeadImage(self.context).image_format

    @property
    def image(self):
        if self.has_image:
            return LeadImage(self.context).get_image()

    @property
    def dimensions(self):
        if self.has_image:
            return LeadImage(self.context).get_image().getImageSize()

    def value(self):
        return self.has_image

    def check(self):
        if not self.value():
            yield ContentCheck(self, 'No lead image found')

# Verifies that a valid lead image format is used for the content
class LeadImageFormat(HasLeadImage):

    title = "Lead Image: Format"

    description = "Lead-images should be either JPEG (for photos) or PNG (for graphics/line art)"

    action = "Please add a quality JPEG or PNG lead image to this content."

    # Sort order (lower is higher)
    sort_order = 5

    # The image format
    def value(self):
        if self.has_image:
            return self.image_format not in ('JPEG', 'PNG')

        return False

    def check(self):
        if self.value():
            yield ContentCheckError(self, 'Invalid format lead image found.')

class LeadImageOrientation(HasLeadImage):

    title = "Lead Image: Orientation"

    description = "Lead-images should be landscape orientation"

    action = "Please add a quality landscape orientation image to this content."

    # Sort order (lower is higher)
    sort_order = 5

    # Check if the image width is less than the height
    def value(self):
        dimensions = self.dimensions

        if dimensions:

            (w,h) = dimensions

            return w < h

        return False


    def check(self):
        if self.value():
            yield ContentCheckError(self, 'Portrait/square orientation lead image found.')

class LeadImageWidth(LeadImageOrientation):

    minimum_image_width = 600

    title = "Lead Image: Width"

    description = "Lead-images should be at least %d pixels wide." % minimum_image_width

    action = "Please add a larger lead image to this content."

    # Check if the image width is less than the height
    def value(self):
        dimensions = self.dimensions

        if dimensions:

            (w,h) = dimensions

            return w < self.minimum_image_width

        return False

    def check(self):

        if self.value():

            (w,h) = self.dimensions

            yield ContentCheckError(self, 'Lead image width is %d pixels.' % w)

# Checks for instances of inappropriate link text in body
class AppropriateLinkText(BodyLinkCheck):

    title = 'HTML: Appropriate Link Text'

    description = "Checks for common issues with link text (e.g. using the URL as link text, 'click here', 'here', etc.)"

    action = "Linked text should be a few words that describe the content that exists at the link."

    find_words = ['click', 'http://', 'https://', 'here',]

    find_words = [x.lower() for x in find_words]

    min_chars = 5 # minimum length of link text.  Arbitrary value of 5

    def value(self):
        data = []

        for a in super(AppropriateLinkText, self).value():
            label = self.soup_to_text(a)
            href = a.get('href', '')

            # Check for a special case where an image is the link, and use the alt text.
            if not label:
                for img in a.findAll('img'):
                    alt = img.get('alt', '')
                    if alt:
                        label = alt
                        break

            data.append((label, href))

        return data

    def check(self):

        # Iterate through link text for document
        for (label, href) in self.value():

            # Minimum length check
            if len(label) < self.min_chars:
                yield ContentCheckError(self, 'Short link text "%s" (%d characters) for %s' % (label, len(label), href))

            # Check for individual prohibited words
            link_words = self.toWords(label)

            # Iterate through the words and check for presence in link text.
            for j in link_words:
                if j in self.find_words:
                    yield ContentCheckError(self, 'Inappropriate Link Text "%s" (found "%s") for %s' % (label, j, href))


# Checks for cases where an image is linked to something
class ExternalAbsoluteImage(BodyImageCheck):

    title = 'HTML: Image with an external or absolute URL'

    description = "Checks for <img> tags that reference images outside the site, or use a URL path rather than Plone's internal method."

    action = "Use the rich text editor to select an image rather than the HTML source code."

    def check(self):
        for img in self.value():
            src = img.get('src', '')
            if not src.startswith('resolveuid'):
                yield ContentCheckError(self, 'Image source of "%s" references an external/absolute image.' % src)


# Checks for cases where a heading has a 'strong' or 'b' tag inside
class BoldHeadings(BodyHeadingCheck):

    title = 'HTML: Bold text inside headings.'

    description = "Headings should not contain bold text."

    action = "Remove bold text from headings"

    def check(self):
        for h in self.value():
            if h.findAll(['strong', 'b']):
                yield ContentCheckError(self, 'Heading %s "%s" contains bold text' % (h.name, self.soup_to_text(h)))


# Checks for cases where a heading has a 'strong' or 'b' tag inside
class HeadingsInBold(BoldHeadings):

    title = 'HTML: Headings inside bold text.'

    description = "Headings should not be inside bold text."

    action = "Remove bold text from around headings"

    def value(self):
        return self.soup.findAll(['strong', 'b'])

    def check(self):
        for b in self.value():
            for h in b.findAll(self.all_heading_tags):
                yield ContentCheckError(self, 'Heading %s "%s" inside bold text' % (h.name, self.soup_to_text(h)))

# Checks for multiple sequential breaks inside a paragraph
class ParagraphMultipleBreakSequenceCheck(BodyTextCheck):

    title = 'HTML: Multiple sequential breaks inside a paragraph.'

    description = "Paragraphs should be contained in individual <p> tags, not separated by 'double breaks.'"

    action = "Replace '<br /><br />' with '</p><p>' in rich text editor."

    def check(self):

        # Iterate through all paragraphs in HTML
        for p in self.soup.findAll('p'):

            # This flag is used to break out of loops early.  It is set if a
            # double break is detected inside a paragraph.  Once we find one,
            # stop checking that paragraph.
            p_has_error = False

            # Iterate through all of the <br /> in the <p>
            for br in p.findAll('br'):

                # Stop looking if we found an error already
                if p_has_error:
                    break

                # Check the next siblings of the <br /> to see if we can find
                # another <br />, skipping whitespace.
                for next_sibling in br.nextSiblingGenerator():

                    # If next sibling is a tag, and the name is 'br', raise an error
                    if isinstance(next_sibling, Tag) and next_sibling.name == 'br':
                        p_text = truncate_text(self.soup_to_text(p), 32)
                        p_has_error = True
                        yield ContentCheckError(self, 'Double breaks found in paragraph beginning with "%s"' % p_text)
                        break
                    # If next sibling is a string, and it is whitespace, keep looking
                    elif isinstance(next_sibling, NavigableString) and not next_sibling.strip():
                        continue
                    # If it's something else, stop looking
                    else:
                        break

# Checks ALL CAPS headings
class AllCapsHeadings(BodyHeadingCheck):

    title = 'HTML: Headings in ALL CAPS.'

    description = "Headings should not use ALL CAPS text."

    action = "Make headings title case."

    def check(self):
        for h in self.value():
            h_text = self.soup_to_text(h)

            # Skip headings that are one-word headings.  They're sometimes acronyms.
            if len(self.toWords(h_text)) > 1:

                if h_text == h_text.upper():
                    yield ContentCheckError(self, '%s heading "%s" has ALL CAPS.' % (h.name, h_text))

# Checks for presence of <u> tag in body text.
class UnderlinedText(BodyTextCheck):

    title = "HTML: Underlined Text"

    description = "Text should not be underlined."

    action = "Remove <u> tag(s) from HTML."

    def check(self):
        for u in self.soup.findAll('u'):
            text = self.soup_to_text(u)
            yield ContentCheckError(self, 'Found underlined text "%s"' % text)


# Checks for presence of inline styles
class InlineStyles(BodyTextCheck):

    title = "HTML: Inline styles"

    description = "Inline styles should not be used."

    action = "Remove inline styles from HTML."

    def check(self):
        for i in self.soup.findAll():
            style = i.get('style', '')
            if style:
                i_text = self.soup_to_text(i)
                yield ContentCheckError(self, 'Inline style "%s" found for %s "%s"' % (style, i.name, i_text)   )

# Checks for presence of inline styles
class ProhibitedAttributes(BodyTextCheck):

    # These attributes are prohibited, except for the values specified.
    attribute_config = {
        'width' : None,
        'height' : None,
        'align' : {
            'p' : ['left'],
            'td' : ['left', 'right', 'center'],
            'th' : ['left', ],
        }
    }

    title = "HTML: Prohibited Attributes"

    description = "Some HTML attributes should not be used."

    action = "Remove these attributes from the HTML."

    def check(self):

        _re = re.compile('\S+')

        for (_attr, ok_values) in self.attribute_config.iteritems():

            for i in self.soup.findAll(attrs={_attr : _re}):

                is_ok = False

                _attr_value = i.get(_attr, None)

                # Null values are fine
                if _attr_value is None:
                    is_ok = True

                # If we're a string
                elif isinstance(_attr_value, (unicode, str)):

                    # Remove whitespace
                    _attr_value = _attr_value.strip()

                    # Empty values are fine
                    if not _attr_value:
                        is_ok = True

                    # If we have an "OK Value" configured, and our value is in
                    # that list, we're fine
                    if ok_values:
                        is_ok = _attr_value in ok_values.get(i.name, [])

                if not is_ok:

                    yield ContentCheckError(self,
                            u'Prohibited attribute (<%s %s="%s" ... />) found.' % (
                            i.name,
                            _attr,
                            _attr_value,
                        )
                    )


# Validate that resolveuid/... links actually resolve, and that they link to a content or a file.
class InternalLinkByUID(BodyLinkCheck):

    title = 'HTML: Internal Links By Plone Id'

    description = "Validation for links using the Plone id rather than a URL."

    action = "Update link to point to valid content."

    def value(self):
        return self.soup.findAll(['a', 'img'])

    @property
    def internal_links(self):

        # Checks for the 'resolveuid' string in the raw HTML
        if 'resolveuid' in self.html:

            # Iterates through the link tags, and grabs the href value
            for a in self.value():

                href = None
                link_type = None

                if a.name in ['a']:
                    href = a.get('href', '')
                    link_type = "Link"
                elif a.name in ['img']:
                    href = a.get('src', '')
                    link_type = "Image"

                # If we found an href...
                if href:

                    # Check for a regex match
                    m = self.resolveuid_re.search(href)

                    if m:
                        # Grab the contents of the href to use in an error message
                        href_text = self.soup_to_text(a)

                        # Pull the UID from the href
                        linked_uid = m.group(1)

                        # Grab the catalog brain by the UID
                        linked_brain = self.uid_to_brain.get(linked_uid, None)

                        # If we found a brain, get the linked object
                        if linked_brain:
                            linked_object = linked_brain.getObject()
                        else:
                            linked_object = None

                        _ = self.object_factory(
                            href=href,
                            text=href_text,
                            uid=linked_uid,
                            brain=linked_brain,
                            object=linked_object,
                            link_type=link_type,
                        )

                        yield(_)

    def check(self):

        # Loop through the links
        for link in self.internal_links:

            # If we didn't find a brain, throw an error
            if not link.brain:
                yield ContentCheckError(self,
                    '%s "%s" does not resolve to a valid object.' % (link.link_type, link.text))

# Check for large images (dimensions, size)
class LargeImages(ContentCheck):

    title = "Large Images"

    description = "Validates that images contained in content are an appropriate size for the web."

    action = "Resize image to a maximum of 1200px width."

    max_width = 1500

    max_size_kb = 2048  # 2MB

    render = True

    def value(self):

        path = '/'.join(self.context.getPhysicalPath())

        v = self.portal_catalog.searchResults({'Type' : 'Image', 'path' : path})

        return [x.getObject() for x in v]

    def dimensions(self, image):
        try:
            return image.image.getImageSize()
        except:
            return (0,0)

    def size(self, image):
        try:
            return image.image.size/1024.0 # KB
        except:
            return 0

    def check(self):
        for v in self.value():

            (w,h) = self.dimensions(v)

            size = self.size(v)

            if w > self.max_width or size > self.max_size_kb:
                yield ContentCheckError(self, u"<a href=\"%s/view\">%s</a> has a width of %dpx, and is %dKB" % (v.absolute_url(), v.title, w, size))

# Validate that active people have valid classification(s)
class ActivePersonClassifications(ContentCheck):

    title = "Person Classifications"

    description = "Validates that people in an Active state are assigned classifications."

    action = "Assign Classifications (e.g. Educator, Faculty, Staff, etc.) to this person."

    def value(self):
        return self.classifications

    def check(self):
        if self.review_state in ['published',] and not self.value():
            yield ContentCheckError(self, u"%s %s has no Classifications." % (
                self.context.Type(),
                self.context.Title()
            ))

# Check for external links.  It doesn't make sense to check external
# links on every save, but this will allow us to do it on-demand if they exist.
class ExternalLinkCheck(BodyLinkCheck):

    # Title for the check
    title = "External Links"

    # Description for the check
    description = "Checks for the presence of external links, and provides a link to run a manual check."

    # Action to remediate the issue
    @property
    def action(self):
        return "<a href=\"%s/@@link_check\">Run an external link check.</a>" % self.context.absolute_url()

    # Timeout
    timeout = 20

    # Render message as HTML
    render = True

    # Render action as HTML
    render_action = True

    @property
    def whitelisted_urls(self):
        return self.registry.get('agsci.common.link_check.whitelist', [])

    def getExternalLinks(self):

        for a in self.getLinks():

            href = a.get('href', '')

            if href:

                (scheme, domain, path) = self.parse_url(href)

                if scheme in ('http', 'https') and domain not in self.bad_domains:
                    yield (href, a.text)

    def value(self):
        return list(set(self.getExternalLinks()))

    # Given a URL, check the whitelist, then the cache, then actualy check it
    def check_link(self, url):

        # Check for whitelist
        if url in self.whitelisted_urls:
            return (200, url)

        # If not, cache it and return it.
        data = self._check_link(url)

        return data

    # Performs the "real" URL check
    def _check_link(self, url, head=False):

        # Set Firefox UA
        headers = requests.utils.default_headers()
        headers['User-Agent'] = u"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0"

        try:

            if head:
                data = requests.head(url, timeout=30, headers=headers)

            else:
                data = requests.get(url, timeout=30, headers=headers)

        except requests.exceptions.HTTPError:
            return (404, url)

        except:
            return (999, url)

        else:

            return_code = data.status_code
            return_url = data.url

            if return_code == 200:

                if self.url_equivalent(url, return_url):
                    return(200, url)
                else:
                    return(302, return_url)

            else:

                if return_code in [301,302]:
                    return(302, return_url)

                else:
                    return (return_code, return_url)

    def check(self):

        if self.value():
            yield ManualCheckError(self,
                u"""Content contains external links."""
            )

    def manual_check(self):

        for (url, link_text) in self.value():

            (return_code, return_url) = self.check_link(url)


            if not link_text:
                link_text = url

            data = self.object_factory(
                title=link_text,
                url=url,
                status=return_code,
                redirect_url=return_url,
            )

            if return_code in (200,):

                yield ContentCheckError(self,
                    u"""<a href=\"%s\">%s</a> is a valid link.""" %
                    (url, link_text), data=data,
                )

            elif return_code in (301, 302,):
                yield ContentCheckError(self,
                    u"""<a href=\"%s\">%s</a> is a <strong>redirect</strong> to <a href=\"%s\">%s</a>""" %
                    (url, link_text, return_url, return_url), data=data,
                )

            elif isinstance(return_code, int) and return_code > 500:
                yield ContentCheckError(self,
                    u"""<a href=\"%s\">%s</a> had a return code of <strong>%d</strong>.""" %
                    (url, link_text, return_code), data=data,
                )

            else:

                yield ContentCheckError(self,
                    u"""<a href=\"%s\">%s</a> had a return code of <strong>%d</strong>.""" %
                    (url, link_text, return_code), data=data,
                )

# Warn if Publishing Dates are in the future
class FuturePublishingDate(ContentCheck):

    # Title for the check
    title = "Future Publishing Date"

    # Description for the check
    description = "Validates that the publishing date for the content is not in the future, which will prevent the content from being visible. This is occasionally the desired behavior, but is often set in error."

    # Action to remediate the issue
    action = "Adjust or remove the publishing date (under the Dates tab) of the content in Plone if it is not set for a reason."

    def value(self):
        return localize(self.context.effective())

    def check(self):
        _ = self.value()

        if _ and _ > self.now:
            yield ContentCheckError(self, u"Publishing Date %s is in the future." % _.strftime('%Y-%m-%d'))

# Checks to see if checks are ignored.
class IgnoredChecks(ContentCheck):

    title = "Ignored Checks"
    description = "Checks to see if any checks are configured to be ignored."
    action = "No action required, this is for reporting purposes only."

    # Sort order (lower is higher)
    sort_order = 1

    def value(self):
        return getattr(self.context.aq_base, 'ignore_checks', [])

    def check(self):
        v = self.value()

        if v:
            yield ManualCheckError(self,
                u"""The following checks are configured to be ignored: %s""" % "; ".join(sorted(v))
            )