try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import ldap
import re

class LDAPInfo(object):

    hosts = [
        'ldap://dirapps.aset.psu.edu',
  #      'ldap://fps.psu.edu'
    ]

    attrs = [
        'cn', 'displayName', 'dn', 'eduPersonAffiliation', 'eduPersonNickname',
        'eduPersonPrimaryAffiliation', 'eduPersonPrincipalName', 'givenName',
        'mail', 'postalAddress', 'psAdminArea', 'psCampus', 'psDepartment',
        'psDirIDN', 'psMailHost', 'psMailID', 'psMailbox', 'psOfficeAddress',
        'psOfficeLocation', 'psOfficePhone', 'sn', 'telephoneNumber', 'title',
        'uid', 'uidNumber',
    ]

    def __init__(self, context, username=None):
        self.context = context
        self.lookup_username = username

    @property
    def username(self):

        # Return the username this is called with if provided
        if self.lookup_username:
            return self.lookup_username

        # Otherwise, grab the username off the 'context'
        username = getattr(self.context, 'username', None)

        if username:
            return username

    def lookup(self):

        try:
            return self.ldap_lookup()
        except:
            pass

    def ldap_lookup(self):

        username = self.username

        if username:

            for host in self.hosts:

                con = ldap.initialize(host)

                if con.simple_bind():
                    base_dn = "dc=psu,dc=edu"

                    _filter = "(uid=%s)" % username

                    results = con.search_s( base_dn, ldap.SCOPE_SUBTREE, _filter, self.attrs )

                    for r in results:
                        (_id, data) = r

                        for (k,v) in data.iteritems():

                            if isinstance(v, (tuple, list)):
                                if len(v) == 1:
                                    data[k] = v[0]

                        data['ldap_host'] = self.ldap_host(host)

                        return data
        return {}

    def is_fps(self, _):
        return _.get('ldap_host', '') == 'fps.psu.edu'

    def get_phone_number(self, ldap_data):

        if self.is_fps(ldap_data):
            return ''

        phone_number = ldap_data.get('psOfficePhone', '')

        if not phone_number:
            _ = ldap_data.get('telephoneNumber', '')

            if _ and isinstance(_, (str, unicode)):

                _re = re.compile('^\s*\+1\s*(\d{3})[\s\-\.]*(\d{3})[\s\-\.]*(\d{4})\s*$')

                m = _re.match(_)

                if m:
                    phone_number = "-".join(m.groups())

        return phone_number

    def get_address(self, ldap_data):

        if self.is_fps(ldap_data):
            return ('', '', '', '')

        # Office Address

        # Blank city/state/zip
        city = state = zip_code = ''

        # Get street address from LDAP data
        street_address = ldap_data.get('postalAddress', '').title()

        # Clean spurious UP in street address
        _up = '$UNIVERSITY PARK$'.title()
        street_address = street_address.replace(_up, '$')

        # Split on $
        street_address = street_address.split('$')

        # Try to extract city/state/zip
        if len(street_address) > 1:

            # Check last line for city, state ZIP
            _csz_re = re.compile("^(.*),\s*(..)\s+([\d\-]+)\s*")

            _csz = _csz_re.match(street_address[-1])

            if _csz:
                (city, state, zip_code) = _csz.groups()
                street_address = street_address[:-1]
                state = state.upper()

        # Join with <cr>
        street_address = "\n".join(street_address)

        # Strip
        street_address = street_address.strip()

        return (street_address, city, state, zip_code)

    def ldap_host(self, _):
        return urlparse(_).netloc
