from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from plone.i18n.normalizer import idnormalizer, filenamenormalizer
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import re
import unicodedata

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