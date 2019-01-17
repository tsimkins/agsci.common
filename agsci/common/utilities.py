from Products.CMFPlone.utils import safe_unicode
from plone.i18n.normalizer import idnormalizer, filenamenormalizer

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