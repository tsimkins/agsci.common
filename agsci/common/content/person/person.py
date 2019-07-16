from Products.CMFCore.utils import getToolByName
from Products.membrane.interfaces import IMembraneUserRoles
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from dexterity.membrane.behavior.user import DxUserObject
from dexterity.membrane.content.member import IMember
from plone.app.content.interfaces import INameFromTitle
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implements, provider, implementer, Interface

from ..behaviors import IContact, ISocialMediaBase

from agsci.common import AgsciMessageFactory as _


ACTIVE_REVIEW_STATES = ('published',)
AGSCI_DIRECTORY_EDITOR = 'agsci.directory.editor'

social_media_fields = [
    'twitter_url', 'facebook_url', 'youtube_url', 'linkedin_url',
]

contact_fields = [
    'email', 'street_address', 'city', 'state',
    'zip_code', 'phone_number',
    'fax_number', 'primary_profile_url',
]

professional_fields = [
    'classifications', 'job_titles', 'hr_job_title', 'hr_admin_area',
    'hr_department', 'all_emails', 'sso_principal_name', 'bio', 'short_bio',
    'education', 'websites', 'areas_expertise', 'research_areas',
]

class ILinkRowSchema(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )

class ILinkDescriptionRowSchema(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=False
    )

    description = schema.TextLine(
        title=_(u"Description"),
        required=False
    )

    url = schema.TextLine(
        title=_(u"URL"),
        required=False
    )


@provider(IFormFieldProvider)
class IPerson(model.Schema, IMember, IContact, ISocialMediaBase):

    __doc__ = "Person Information"

    # Fieldsets

    model.fieldset(
        'contact',
        label=_(u'Contact Information'),
        fields=contact_fields,
    )

    model.fieldset(
        'professional',
        label=_(u'Professional Information'),
        fields=professional_fields,
    )

    model.fieldset(
        'social-media',
        label=_(u'Social Media'),
        fields=social_media_fields,
    )

    form.omitted(
        'homepage', 'hr_job_title', 'hr_admin_area',
        'hr_department', 'all_emails', 'sso_principal_name'
    )

    # Grid Fields
    form.widget(websites=DataGridFieldFactory)

    # Only allow Directory Editors to write to these fields
    form.write_permission(username=AGSCI_DIRECTORY_EDITOR)
    form.write_permission(classifications=AGSCI_DIRECTORY_EDITOR)
    form.write_permission(primary_profile_url=AGSCI_DIRECTORY_EDITOR)

    # Fields
    username = schema.TextLine(
        title=_(u"Penn State Username"),
        description=_(u"Of format 'xyz123'"),
        required=True,
    )

    first_name = schema.TextLine(
        title=_(u"First Name"),
        required=True,
    )

    middle_name = schema.TextLine(
        title=_(u"Middle Name"),
        required=False,
    )

    last_name = schema.TextLine(
        title=_(u"Last Name"),
        required=True,
    )

    suffix = schema.TextLine(
        title=_(u"Suffix"),
        required=False,
    )

    classifications = schema.List(
        title=_(u"Classifications"),
        required=True,
        value_type=schema.Choice(vocabulary="agsci.common.person.classifications"),
    )

    job_titles = schema.List(
        title=_(u"Job Titles"),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    hr_job_title = schema.TextLine(
        title=_(u"HR Job Title"),
        required=False,
    )

    hr_admin_area = schema.TextLine(
        title=_(u"HR Admin Area"),
        required=False,
    )

    hr_department = schema.TextLine(
        title=_(u"HR Department"),
        required=False,
    )

    all_emails = schema.Tuple(
        title=_(u"All Penn State Email Addresses"),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    sso_principal_name = schema.TextLine(
        title=_(u"SSO Principal Name"),
        required=False,
    )

    education = schema.List(
        title=_(u"Education"),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    websites = schema.List(
        title=u"Websites",
        description=u"",
        value_type=DictRow(title=u"Website", schema=ILinkRowSchema),
        required=False
    )

    areas_expertise = schema.List(
        title=_(u"Areas of Expertise"),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    research_areas = schema.List(
        title=_(u"Research Areas"),
        required=False,
        value_type=schema.Choice(vocabulary="agsci.common.research_areas"),
    )

    primary_profile_url = schema.TextLine(
        title=_(u"Primary Profile URL"),
        description=_(u"URL of primary profile (if not Extension site)"),
        required=False,
    )

    short_bio = RichText(
        title=_(u"Short Biography"),
        description=_(u"Used in listings."),
        required=False,
    )

# Configuring default roles with Dexterity
# http://docs.plone.org/develop/plone/members/membrane.html#id11

DEFAULT_ROLES = ['Member']

@implementer(IMembraneUserRoles)
@adapter(IPerson)
class PersonDefaultRoles(DxUserObject):

    def getRolesForPrincipal(self, principal, request=None):

        # Check if person is active
        wftool = getToolByName(self.context, 'portal_workflow')

        # Get workflow state
        review_state = wftool.getInfoFor(self.context, 'review_state')

        # Validate that person is published
        if review_state in ['published',]:

            # Get classifications for person
            classifications = getattr(self.context, 'classifications', [])

            # If the person has classification, but isn't a volunteer, they're a Member
            if classifications:
                return DEFAULT_ROLES

        # Default to no default roles
        return []

# Calculate "Title" as person name
# Based on http://davidjb.com/blog/2010/04/plone-and-dexterity-working-with-computed-fields/

class Person(Item):

    name_fields = ['first_name', 'middle_name', 'last_name', 'suffix']

    @property
    def name_data(self):
        from agsci.common import object_factory
        names = dict([(x, getattr(self, x, '')) for x in self.name_fields])
        names['title'] = self.title
        return object_factory(**names)

    @property
    def title(self):

        names = [getattr(self, x, '') for x in self.name_fields[:-1]] # Not suffix

        v = " ".join([x.strip() for x in names if x])

        if getattr(self, 'suffix', ''):
            v = "%s, %s" % (v, self.suffix.strip())

        return v

    def setTitle(self, value):
        return

    def getSortableName(self):
        fields = ['last_name', 'first_name', 'middle_name', ]
        return tuple([getattr(self, x, '') for x in fields])


class ITitleFromPersonUserId(INameFromTitle):
    def title():
        """Return a processed title"""

class TitleFromPersonUserId(object):
    implements(ITitleFromPersonUserId)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return self.context.username