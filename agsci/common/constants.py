import re

# Naively assume that all dates are in Eastern time
DEFAULT_TIMEZONE = 'US/Eastern'

# Mimetype to PIL and filename extension
IMAGE_FORMATS = {
    'image/jpeg' : ['JPEG', 'jpg'],
    'image/png' : ['PNG', 'png'],
    'image/gif' : ['GIF', 'gif'],
    'image/x-ms-bmp' : ['BMP', 'bmp'],
}

# File extensions lookup hardcoded, so we don't have to use mimetypes_registry
MIMETYPE_EXTENSIONS = {
    u'application/pdf': u'pdf',
    u'application/vnd.ms-excel': u'xls',
    u'application/vnd.ms-excel.sheet.macroEnabled.12': u'xlsm',
    u'application/vnd.ms-powerpoint': u'ppt',
    u'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': u'xlsx',
    u'application/vnd.openxmlformats-officedocument.wordprocessingml.document': u'docx',
    u'image/gif': u'gif',
    u'image/jpeg': u'jpg',
    u'image/png': u'png',
}

AGSCI_DOMAIN = "mS5J5CtL4kuPKm7P.agsci.psu.edu"

CMS_DOMAIN = "r39JxvLi.cms.extension.psu.edu"

DEPARTMENT_CONFIG_URL = 'http://%s/extension-config/config.json' % CMS_DOMAIN

ASSETS_DOMAIN = "assets.agsci.psu.edu"

# Domains for the Plone site based on site.getId()
DOMAIN_CONFIG = {
    'agsci' : 'agsci.psu.edu',
    'private-internal': "agsci.psu.edu",
    'ento.psu.edu': 'ento.psu.edu',
    'plantscience.psu.edu': 'plantscience.psu.edu',
    'foodscience.psu.edu': 'foodscience.psu.edu',
    'aese.psu.edu': 'aese.psu.edu',
    'abe.psu.edu': 'abe.psu.edu',
    'animalscience.psu.edu': 'animalscience.psu.edu',
    'ecosystems.psu.edu': 'ecosystems.psu.edu',
    'plantpath.psu.edu': 'plantpath.psu.edu',
    'vbs.psu.edu': 'vbs.psu.edu',
    '4-h' : 'extension.psu.edu',
    'nutrient-management' : 'extension.psu.edu',
    'rule' : 'extension.psu.edu',
    'mwon' : 'extension.psu.edu',
    'watershed-stewards' : 'extension.psu.edu',
    'master-gardener' : 'extension.psu.edu',
    'betterkidcare' : 'extension.psu.edu',
}

RESOLVEUID_RE = re.compile("(?:\.\./)*resolveuid/([abcdef0-9]{32})", re.I|re.M)
