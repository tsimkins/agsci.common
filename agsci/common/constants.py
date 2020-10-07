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

DEPARTMENT_CONFIG_URL = 'http://r39JxvLi.cms.extension.psu.edu/extension-config/config.json'

AGSCI_DOMAIN = "mS5J5CtL4kuPKm7P.agsci.psu.edu"

ASSETS_DOMAIN = "assets.agsci.psu.edu"
#ASSETS_DOMAIN = "localhost:5051"