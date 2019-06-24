from datetime import datetime
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer, filenamenormalizer
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import htmlentitydefs
import pytz
import re
import unicodedata

from .constants import DEFAULT_TIMEZONE

#Ploneify
def ploneify(toPlone, filename=False):

    # Start with Unicode
    ploneString = safe_unicode(toPlone)

    # Replace specific characters that aren't caught by the unicode transform
    for (_f, _t) in [
        # Various dash-y characters
        (u'\u2010', u'-'),
        (u'\u2011', u'-'),
        (u'\u2012', u'-'),
        (u'\u2013', u'-'),
        (u'\u2014', u'-'),
        (u'\u2015', u'-'),
    ]:
        ploneString = ploneString.replace(_f, _t)

    # Convert accented characters to ASCII
    # Ref: https://stackoverflow.com/questions/14118352/how-to-convert-unicode-accented-characters-to-pure-ascii-without-accents
    ploneString = unicodedata.normalize('NFD', ploneString).encode('ascii', 'ignore')

    # Normalize using the system utility
    if filename:
        ploneString = filenamenormalizer.normalize(ploneString, max_length=99999)
        ploneString = re.sub('[-\s]+', '_', ploneString) # Replace whitespace with underscores
    else:
        ploneString = idnormalizer.normalize(ploneString, max_length=99999)

    # Remove leading/trailing dashes
    ploneString = re.sub("-$", "", ploneString)
    ploneString = re.sub("^-", "", ploneString)

    return ploneString

def toLocalizedTime(time, long_format=None, time_only=None, end_time=None, format=None):

    def friendly(d):

        if not d:
            return ''

        if d.startswith('0'):
            d = d.replace('0', '', 1)

        d = d.replace('12:00 AM', '').strip()

        return d.replace(' 0', ' ')

    # Converts a timestamp to a DateTime object.
    # If it's a GMT time, convert that to US/Eastern
    def toDateTime(t):

        if not isinstance(t, DateTime):
            t = DateTime(t)

        if t.timezone() == 'GMT+0':
            t = t.toZone('US/Eastern')

        return t

    if not time:
        return ''

    def fmt(t, long_format=None, time_only=None, format=None):

        if format:
            return friendly(t.strftime(format))

        if time_only:
            return friendly(t.strftime('%I:%M %p'))

        elif long_format:
            return friendly(t.strftime('%B %d, %Y %I:%M %p'))

        return friendly(t.strftime('%B %d, %Y'))

    # Handle error when converting invalid times.

    try:
        start_full_fmt = fmt(time, long_format, time_only, format)
    except ValueError:
        return ''

    if end_time:
        try:
            end_full_fmt = fmt(end_time, long_format, time_only, format)
        except ValueError:
            return ''

        start = toDateTime(time)
        end = toDateTime(end_time)

        start_date_fmt = start.strftime('%Y-%m-%d')
        end_date_fmt = end.strftime('%Y-%m-%d')

        start_time_fmt = start.strftime('%H:%M')
        end_time_fmt = end.strftime('%H:%M')

        # If the same date
        if start_date_fmt == end_date_fmt:

            # If we want the long format, return [date] [time] - [time]
            if long_format:
                if start_time_fmt == end_time_fmt:
                    return start_full_fmt
                elif start_time_fmt == '00:00':
                    return end_full_fmt
                elif end_time_fmt == '00:00':
                    return start_full_fmt
                else:
                    return '%s, %s - %s' % (
                        toLocalizedTime(time),
                        toLocalizedTime(time, time_only=1),
                        toLocalizedTime(end_time, time_only=1)
                    )

            # if time_only
            elif time_only:
                if start_full_fmt and end_full_fmt:
                    if start_full_fmt == end_full_fmt:
                        return start_full_fmt
                    else:
                        return '%s - %s' % (start_full_fmt, end_full_fmt)
                elif start_full_fmt:
                    return start_full_fmt
                elif end_full_fmt:
                    return end_full_fmt
                else:
                    return ''

            # Return the start date in short format
            else:
                return start_full_fmt
        else:
            default_repr = '%s to %s' % (friendly(start_full_fmt), friendly(end_full_fmt))

            if long_format:
                return default_repr

            elif time_only:

                if start_full_fmt and end_full_fmt:
                    if start_full_fmt == end_full_fmt:
                        return start_full_fmt
                    else:
                        return '%s - %s' % (start_full_fmt, end_full_fmt)
                elif start_full_fmt:
                    return start_full_fmt
                elif end_full_fmt:
                    return end_full_fmt
                else:
                    return ''
            elif start.year() == end.year():
                if start.month() == end.month():
                    return '%s %d-%d, %d' % (start.strftime('%B'), start.day(), end.day(), start.year())
                else:
                    return '%s %d - %s %d, %d' % (start.strftime('%B'), start.day(), end.strftime('%B'), end.day(), start.year())
            else:
                return default_repr

    else:
        try:
            return fmt(time, long_format, time_only, format)
        except ValueError:
            return ''

def getVocabularyTerms(context, vocabulary_name):
    factory = getUtility(IVocabularyFactory, vocabulary_name)
    vocab = factory(context)
    return [x.value for x in vocab._terms]

# https://stackoverflow.com/questions/12178669/list-the-fields-of-a-dexterity-object
def get_fields_by_type(portal_type):
    fti = getUtility(IDexterityFTI, name=portal_type)
    schema = fti.lookupSchema()
    fields = schema.namesAndDescriptions()
    for bname in fti.behaviors:
        factory = getUtility(IBehavior, bname)
        behavior = factory.interface
        fields += behavior.namesAndDescriptions()
    return dict(fields)

def toBool(_):
    if isinstance(_, bool):
        return _
    if isinstance(_, (str, unicode)):
        return _.lower().strip() in ('true', '1')
    if isinstance(_, int):
        return bool(_)
    return False

# This makes the 'getURL' and 'absolute_url', etc. methods return the proper
# URL through the debug prompt.
def setSiteURL(site, domain='trs22.psu.edu:5051', path='', https=True):

    if path and not path.startswith('/'):
        path = '/%s' % path

    if https:
        url = 'https://%s%s' % (domain, path)
    else:
        url = 'http://%s%s' % (domain, path)

    if url.endswith('/'):
        url = url[:-1]

    site.REQUEST['SERVER_URL'] = url

    site.REQUEST.other['VirtualRootPhysicalPath'] = site.getPhysicalPath()

    if site.REQUEST.get('_ec_cache', None):
        site.REQUEST['_ec_cache'] = {}

def truncate_text(v, max_chars=200, el='...'):

    if v and isinstance(v, (str, unicode)):

        v = " ".join(v.strip().split())

        if len(v) > max_chars:
            v = v[:max_chars]
            _d = v.split()
            _d.pop()
            v = " ".join(_d) + el

    return v

# Localize all DateTime/datetime values to Eastern Time Zone
def localize(_):

    tz = pytz.timezone(DEFAULT_TIMEZONE)

    if isinstance(_, DateTime):

        try:
            tz = pytz.timezone(_.timezone())
        except pytz.UnknownTimeZoneError:
            pass

        _ = _.asdatetime()

    if isinstance(_, datetime):

        if not _.tzinfo:
            return tz.localize(_)

        return _

    return None

# Clean up 'gunk' characters in HTML
def scrub_html(html):

    # Clean up whitespace, and make everything space delimited
    html = " ".join(html.split())

    # HTML entites to turn into ASCII.
    htmlEntities = [
        ["&#8211;", "--"],
        ["&#8220;", '"'],
        ["&#8221;", '"'],
        ["&#8216;", "'"],
        ["&#8217;", "'"],
        ["&#145;", "'"],
        ["&#146;", "'"],
        ["&#160;", " "],
        ["&nbsp;", " "],
        ["&bull;", " "],
        ["&quot;", "\""],
        ["&#150;", "-"],
        ["&#151;", " -- "],
        ["&#147;", "\""],
        ["&#148;", "\""],
        ["&quot;", "\""],
        ["&quot;", "\""],
        [unichr(186), "&deg;"],
        [unichr(176), "&deg;"],
        [unichr(215), "x"],
        ["`", "'"],
        [unichr(181), "&micro;"],
        [unichr(8776), "&asymp;"],
        [unichr(160), " "],
        ["\t", " "],
        [u"\u201c", '"'],
        [u"\u201d", '"'],
        [u"\u2018", "'"],
        [u"\u2019", "'"],
        [u"\u2013", "-"],
        [u"\u2014", "--"],
    ]

    # Replace those entites
    for ent in htmlEntities:
        html = html.replace(ent[0], ent[1])

    # Replace unicode characters (u'\u1234') with html entity ('&abcd;')
    for (k,v) in htmlentitydefs.codepoint2name.iteritems():

        if v in ["gt", "lt", "amp", "bull", "quot"]:
            continue

        html = html.replace(unichr(k), "&%s;" % v)

    # Replace <br /> inside table th/td with nothing.
    replaceEmptyBR = re.compile(r'(<(td|th).*?>)\s*(<br */*>\s*)+\s*(</\2>)', re.I|re.M)
    html = replaceEmptyBR.sub(r"\1 \4", html)

    # Remove HTML elements that only have a <br /> inside them
    removeEmptyBR = re.compile(r'(<(p|div|strong|em)>)\s*(<br */*>\s*)+\s*(</\2>)', re.I|re.M)
    html = removeEmptyBR.sub(r" ", html)

    # Remove attributes that should not be transferred
    removeAttributes = re.compile('\s*(id|width|height|valign|type|style|target|dir)\s*=\s*".*?"', re.I|re.M)
    html = removeAttributes.sub(" ", html)

    # Remove empty tags
    removeEmptyTags = re.compile(r'<(p|span|strong|em)>\s*</\1>', re.I|re.M)
    html = removeEmptyTags.sub(" ", html)

    # Remove HTML comments
    removeComments = re.compile(r'<!--(.*?)-->', re.I|re.M)
    removeCommentsEncoded = re.compile(r'&lt;!--(.*?)--&gt;', re.I|re.M)

    html = removeComments.sub(" ", html)
    html = removeCommentsEncoded.sub(" ", html)

    # Return of scrubbed HTML
    return html