from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from DateTime import DateTime
from OFS.Folder import Folder
from PIL import Image
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.Portal import PloneSite
from datetime import datetime
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer, filenamenormalizer
from plone.namedfile.file import NamedBlobImage
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory

try:
    from plone.base.utils import safe_text as safe_unicode
except ImportError:
    from Products.CMFPlone.utils import safe_unicode

import hashlib
import pytz
import re
import requests
import unicodedata

try:
    from AccessControl.users import UnrestrictedUser as BaseUnrestrictedUser
except ImportError:
    try:
        from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
    except ImportError:
        from AccessControl.User import Super as BaseUnrestrictedUser

try:
    import html.entities as htmlentitydefs
except ImportError:
    import htmlentitydefs

try:
    from StringIO import StringIO ## for Python 2
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO, StringIO ## for Python 3

from .constants import DEFAULT_TIMEZONE, DEPARTMENT_CONFIG_URL, DOMAIN_CONFIG, IMAGE_FORMATS

DEFAULT_ROLES = ['Contributor', 'Reviewer', 'Editor', 'Reader']

#Ploneify
def ploneify(toPlone, filename=False):

    if not toPlone:
        return ''

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
    ploneString = safe_unicode(unicodedata.normalize('NFD', ploneString).encode('ascii', 'ignore'))

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

def getVocabularyTerms(context, vocabulary_name=None, vocabulary=None):

    if vocabulary_name:
        factory = getUtility(IVocabularyFactory, vocabulary_name)
        _ = factory(context)

    elif vocabulary:
        _ = vocabulary

    return [x.value for x in _._terms]

def getBases(_):
    rv = []

    for __ in _.getBases():
        rv.append(__)
        rv.extend(getBases(__))

    return rv

# https://stackoverflow.com/questions/12178669/list-the-fields-of-a-dexterity-object
def get_fields_by_type(portal_type):

    fti = getUtility(IDexterityFTI, name=portal_type)
    schema = fti.lookupSchema()
    fields = list(schema.namesAndDescriptions())

    for _schema in getBases(schema):
        fields += _schema.namesAndDescriptions()

    for bname in fti.behaviors:
        factory = getUtility(IBehavior, bname)
        behavior = factory.interface
        fields += behavior.namesAndDescriptions()

        for _behavior in getBases(behavior):
            fields += _behavior.namesAndDescriptions()

    return dict(fields)

def toBool(_):
    if isinstance(_, bool):
        return _
    if isinstance(_, str):
        return _.lower().strip() in ('true', '1')
    if isinstance(_, int):
        return bool(_)
    return False

def truncate_text(v, max_chars=200, el='...'):

    if v and isinstance(v, str):

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
            _ = datetime(
                _.year(), _.month(), _.day(),
                _.hour(), _.minute(), int(_.second())
            )
        else:
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
        [chr(186), "&deg;"],
        [chr(176), "&deg;"],
        [chr(215), "x"],
        ["`", "'"],
        [chr(181), "&micro;"],
        [chr(8776), "&asymp;"],
        [chr(160), " "],
        ["\t", " "],
        [u"\u201c", '"'],
        [u"\u201d", '"'],
        [u"\u2018", "'"],
        [u"\u2019", "'"],
        [u"\u2013", "-"],
        [u"\u2014", "--"],
        [u'\u2022', "* "],
    ]

    # Replace those entites
    for ent in htmlEntities:
        html = html.replace(ent[0], ent[1])

    # Replace unicode characters (u'\u1234') with html entity ('&abcd;')
    for (k,v) in htmlentitydefs.codepoint2name.items():

        if v in ["gt", "lt", "amp", "bull", "quot"]:
            continue

        html = html.replace(chr(k), "&%s;" % v)

    # Replace <br /> inside table th/td with nothing.
    replaceEmptyBR = re.compile(r'(<(td|th).*?>)\s*(<br */*>\s*)+\s*(</\2>)', re.I|re.M)
    html = replaceEmptyBR.sub(r"\1 \4", html)

    # Remove HTML elements that only have a <br /> inside them
    removeEmptyBR = re.compile(r'(<(p|div|strong|em)>)\s*(<br */*>\s*)+\s*(</\2>)', re.I|re.M)
    html = removeEmptyBR.sub(r" ", html)

    # Fix paragraphs that have duplicate <br /> tags
    replaceDuplicateBR = re.compile(r'(<p.*?>)(.*?)(<br */*>\s*){2,10}(.*?)(</p>)', re.I|re.M)
    paragraph = re.compile(r'(<p.*?>.*?</p>)', re.I|re.M)

    replacements = []

    for m in paragraph.finditer(html):
        p = m.group(0)
        p_orig = p

        while replaceDuplicateBR.search(p):
            p = replaceDuplicateBR.sub(r"\1\2\5 \1\4\5", p)
        if p != p_orig:
            replacements.append([p_orig, p])

    for (old, new) in replacements:
        html = html.replace(old, new)

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

class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()

def execute_under_special_role(roles, function, *args, **kwargs):
    """ Execute code under special role privileges.

    Example how to call::

        execute_under_special_role(portal, "Manager",
            doSomeNormallyNotAllowedStuff,
            source_folder, target_folder)


    @param portal: Reference to ISiteRoot object whose access controls we are using

    @param function: Method to be called with special privileges

    @param roles: User roles for the security context when calling the privileged code; e.g. "Manager".

    @param args: Passed to the function

    @param kwargs: Passed to the function
    """

    portal = getSite()
    sm = getSecurityManager()

    try:
        try:
            # Clone the current user and assign a new role.
            # Note that the username (getId()) is left in exception
            # tracebacks in the error_log,
            # so it is an important thing to store.
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', roles, ''
                )

            # Wrap the user in the acquisition context of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)

# Set roles on object
def set_editor_roles(context, group_id, roles=DEFAULT_ROLES):
    context.manage_setLocalRoles(group_id, roles)
    context.reindexObjectSecurity()

# Adds an editors group to the subsite
def add_editors_group(context):
    group_id = "%s-editors"% str(context.id)
    group_title = "%s Editors"% str(context.Title())

    grouptool = getToolByName(context, 'portal_groups')

    if grouptool.addGroup(group_id):
        grouptool.getGroupById(group_id).title = group_title

    set_editor_roles(context, group_id)

    return group_id

def get_portlet_manager(context, manager_name):
    return getUtility(IPortletManager, name=manager_name, context=context)

def get_portlet_assignment_manager(context, manager_name):
    manager = get_portlet_manager(context, manager_name)
    return getMultiAdapter((context, manager), ILocalPortletAssignmentManager)

def get_portlet_mapping(context, manager_name):
    manager = get_portlet_manager(context, manager_name)
    return getMultiAdapter((context, manager), IPortletAssignmentMapping)

def getPloneSites(app, l=0, ids=[]):

    sites = []

    if ids:
        ids = [x.replace('.psu.edu', '') for x in ids]
        ids.extend(['%s.psu.edu' % x for x in ids])

    if l <= 1:

        for (_id, _) in app.ZopeFind(app):
            if isinstance(_, PloneSite):
                if _.getId() in ids or not ids:
                    sites.append(_)
            elif isinstance(_, Folder):
                sites.extend(getPloneSites(_, l+1, ids=ids))

    return sorted(sites, key=lambda x: x.getId())

# This makes the 'getURL' and 'absolute_url', etc. methods return the proper
# URL through the debug prompt.
def setSiteURL(site, domain=None, path='', https=True, edit=False):

    if not domain:
        domain = DOMAIN_CONFIG.get(site.getId(), 'nohost_%s_' % site.getId())

    if edit:
        if domain.startswith('extension.'):
            domain = 'sites.%s' % domain
        elif not domain.startswith('edit.'):
            domain = 'edit.%s' % domain

    if not path:
        path = {
            'private-internal' : '/inside',
            '4-h' : '/programs/4-h',
            'nutrient-management' : '/programs/nutrient-management',
            'rule' : '/programs/rule',
            'mwon' : '/programs/mwon',
            'watershed-stewards' : '/programs/watershed-stewards',
            'master-gardener' : '/programs/master-gardener',
            'betterkidcare' : '/programs/betterkidcare',
            'associations' : '/associations',
            'career-day' : '/career-day',
            'paonestop' : '/programs/paonestop',
            'snap-ed' : '/programs/snap-ed',
            'web' : '/intranet/web',
        }.get(site.getId(), path)

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

def toISO(v):

    if isinstance(v, DateTime):
        try:
            tz = pytz.timezone(v.timezone())
        except pytz.UnknownTimeZoneError:
            # Because that's where we are.
            tz = pytz.timezone(DEFAULT_TIMEZONE)

        tmp_date = datetime(v.year(), v.month(), v.day(), v.hour(),
                            v.minute(), int(v.second()))

        if tmp_date.year not in [2499, 1000]:
            return tz.localize(tmp_date).isoformat()

    elif isinstance(v,datetime):
        return v.isoformat()

    return None

def getNavigationViewlet():
    # Avoid circular import
    from .browser.viewlets import NavigationViewlet

    # Call navigation viewlet
    return NavigationViewlet(getSite(), getRequest(), None)

def getDepartmentId():

    viewlet = getNavigationViewlet()
    return viewlet.department_id

def getExtensionConfig(department_id=None, category=None):

    rv = []

    if not department_id:
        department_id = getDepartmentId()

    # If we have a department id, get the config from the CMS
    if department_id:

        try:
            data = requests.get(DEPARTMENT_CONFIG_URL).json()

        except:
            pass

        else:

            if department_id in data:

                for k in ('categories', 'products'):

                    if k in data[department_id]:

                        # If there's a category provided, filter by category
                        if category:
                            for _ in data[department_id][k]:
                                _l1 = _.get('CategoryLevel1', [])
                                if _l1 and category in _l1:
                                    rv.append(_)
                        else:
                            rv.extend(data[department_id][k])

    return rv

def md5sum(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

# Resize image to new dimensions.  This takes the 'blob' field for the image,
# checks to see if it falls within the dimensions, and scales it accordingly.
# (from agsci.atlas.utilities)

def rescaleImage(image, max_width=1200.0, max_height=1200.0, quality=100):

    img_value = scaleImage(image, max_width=max_width, max_height=max_height, quality=quality)

    if img_value:
        image._setData(img_value)
        return True

def scaleImage(image, max_width=1200.0, max_height=1200.0, quality=100):

    # Test the field to make sure it's a blob image
    if not isinstance(image, NamedBlobImage):
        raise TypeError(u'%r is not a NamedBlobImage field.' % image)

    (w,h) = image.getImageSize()

    image_format = IMAGE_FORMATS.get(image.contentType, [None, None])[0]

    ratio = min([float(max_width)/w, float(max_height)/h])

    if ratio < 1.0 or quality < 100:

        if ratio < 1.0:
            new_w = w * ratio
            new_h = h * ratio
        else:
            new_w = w
            new_h = h

        try:
            pil_image = Image.open(BytesIO(image.data))
        except IOError:
            pass
        else:
            pil_image.thumbnail([new_w, new_h], Image.ANTIALIAS)

            img_buffer = BytesIO()

            pil_image.save(img_buffer, image_format, quality=quality)

            return img_buffer.getvalue()
