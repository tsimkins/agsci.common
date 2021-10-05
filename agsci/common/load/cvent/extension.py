from . import ImportCventView as _ImportCventView
from agsci.common.constants import CMS_DOMAIN

# Cvent Import View for Extension
class ImportCventView(_ImportCventView):

    email_users = ['trs22', ]

    @property
    def calendar_url(self):
        uid = self.uid

        if not uid:
            raise ValueError("No 'id' parameter Provided")

        return "http://%s/cvent-extension/%s" % (CMS_DOMAIN, uid)

    @property
    def uid(self):
        return self.request.get('id', None)