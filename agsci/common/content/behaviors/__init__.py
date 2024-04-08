from dexterity.membrane.content.member import is_email
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

@provider(IFormFieldProvider)
class IAlwaysExcludeFromNavigation(model.Schema):
    pass

@provider(IFormFieldProvider)
class IDefaultExcludeFromNavigation(IExcludeFromNavigation):

    form.write_permission(exclude_from_nav="cmf.ManagePortal")

    exclude_from_nav = schema.Bool(
        title=_(
            u'label_exclude_from_nav',
            default=u'Exclude from navigation'
        ),
        description=_(
            u'help_exclude_from_nav',
            default=u'If selected, this item will not appear in the '
                    u'navigation tree'
        ),
        default=True,
        required=False,
    )

@provider(IFormFieldProvider)
class IResearchAreas(model.Schema):

    department_research_areas = schema.List(
        title=_(u"Research Areas"),
        description=_(u""),
        value_type=schema.TextLine(required=True),
        required=False,
    )


@provider(IFormFieldProvider)
class ISEO(model.Schema):

    form.write_permission(exclude_from_robots="cmf.ManagePortal")

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=[
            'canonical_url_text',
            'exclude_from_robots',
        ],
    )

    canonical_url_text = schema.TextLine(
        title=_(u"Canonical URL (External Resource)"),
        description=_(u"Full URL"),
        required=False,
    )

    exclude_from_robots = schema.Bool(
        title=_(u"Exclude from search engines"),
        description=_(u"Add to robots.txt file and add meta tag to header."),
        required=False,
    )


@provider(IFormFieldProvider)
class INewsItemFields(model.Schema):

    article_link = schema.TextLine(
        title=_(u"Article URL"),
        description=_(u"Use this field if the article lives at another place on the internet. Do not copy/paste the full article text from another source."),
        required=False,
    )


@provider(IFormFieldProvider)
class IFolderFields(model.Schema):

    form.write_permission(search_section="cmf.ManagePortal")

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=[
            'show_date',
            'show_description',
            'show_image',
            'search_section',
            'show_subfolder_text',
            'browser_title',
            'browser_org_title',
        ],
    )

    show_date = schema.Bool(
        title=_(u"Show date"),
        description=_(u"This will show the publication date for each item in the folder listing."),
        required=False,
        default=False,
    )

    show_description = schema.Bool(
        title=_(u"Show description"),
        description=_(u"This will show the description for each item in the folder listing."),
        required=False,
        default=True,
    )

    show_image = schema.Bool(
        title=_(u"Show Lead Image in folder listing"),
        description=_(u"This will show the lead image for each item in the folder listing."),
        required=False,
        default=True,
    )

    search_section = schema.Bool(
        title=_(u"Search section"),
        description=_(u"This defaults the search to searching this section rather than site-wide."),
        required=False,
        default=False,
    )

    browser_title = schema.Bool(
        title=_(u"Include in browser title?"),
        description=_(u"Use this folder as an intermediate level in the \"title\" attribute."),
        required=False,
        default=False,
    )

    browser_org_title = schema.Bool(
        title=_(u"Use this as 'site' title?"),
        description=_(u"Use this folder to display the 'site' portion of the title, rather than the actual site title. Caution: This overrides the college/department."),
        required=False,
        default=False,
    )

    show_subfolder_text = schema.Bool(
        title=_(u"Show text of folders in Subfolder View"),
        description=_(u""),
        required=False,
        default=False,
    )

@provider(IFormFieldProvider)
class IHomepageFields(model.Schema):
    pass


@provider(IFormFieldProvider)
class IEventFields(model.Schema):

    model.fieldset(
        'registration',
        label=_(u'Registration'),
        fields=[
            'free_registration',
            'free_registration_attendee_limit',
            'free_registration_confirmation_message',
            'free_registration_deadline',
            'free_registration_email',
        ],
    )

    event_canceled = schema.Bool(
        title=_(u"This event has been canceled"),
        description=_(u"Check this box if an event has been canceled, and provide any addition information under 'Event Cancellation Information'"),
        required=False,
    )

    event_canceled_info = RichText(
        title=_(u"Event Cancellation Information"),
        description=_(u""),
        required=False,
    )

    free_registration = schema.Bool(
        title=_(u"Enable online event registration (for no-fee events only)."),
        description=_(u""),
        required=False,
    )

    free_registration_attendee_limit = schema.Int(
        title=_(u"Maximum Attendees"),
        description=_(u"Additional registrations not be permitted after this number of registrations."),
        required=False,
    )

    free_registration_confirmation_message = RichText(
        title=_(u"Email Confirmation Message"),
        description=_(u"Additional text sent as part of confirmation email."),
        required=False,
    )

    free_registration_deadline = schema.Datetime(
        title=_(u"Registration deadline."),
        description=_(u"Registrations will not be permitted after this date."),
        required=False,
    )

    free_registration_email = schema.TextLine(
        title=_(u"Email address for registration responses."),
        description=_(u"Use this field if you would like to receive an email for each registration."),
        required=False,
    )

    map_link = schema.TextLine(
        title=_(u"Map To Location"),
        description=_(u"e.g. Google Maps link"),
        required=False,
    )


class ISocialMediaBase(model.Schema):

    __doc__ = "Social Media"

    form.write_permission(newsletter_url="cmf.ManagePortal")

    facebook_url = schema.TextLine(
        title=_(u"Facebook URL"),
        required=False,
    )

    twitter_url = schema.TextLine(
        title=_(u"X (Twitter) URL"),
        required=False,
    )

    youtube_url = schema.TextLine(
        title=_(u"YouTube URL"),
        required=False,
    )

    instagram_url = schema.TextLine(
        title=_(u"Instagram URL"),
        required=False,
    )

    linkedin_url = schema.TextLine(
        title=_(u"LinkedIn URL"),
        required=False,
    )

    newsletter_url = schema.TextLine(
        title=_(u"Newsletter Subscribe URL"),
        required=False,
    )


@provider(IFormFieldProvider)
class ILocation(model.Schema):

    __doc__ = "Location Data"

    street_address = schema.List(
        title=_(u"Street Address"),
        required=False,
        value_type=schema.TextLine(required=False),
    )

    city = schema.TextLine(
        title=_(u"City"),
        required=False,
    )

    state = schema.Choice(
        title=_(u"State"),
        vocabulary="agsci.common.states",
        required=False,
    )

    zip_code = schema.TextLine(
        title=_(u"ZIP Code"),
        required=False,
    )

@provider(IFormFieldProvider)
class IContact(ILocation):

    __doc__ = "Contact Information"

    phone_number = schema.TextLine(
        title=_(u"Phone Number"),
        required=False,
    )

    fax_number = schema.TextLine(
        title=_(u"Fax Number"),
        required=False,
    )

    email = schema.TextLine(
        title=_(u'E-mail Address'),
        required=False,
        constraint=is_email,
    )

class ISocialContact(ISocialMediaBase, IContact):

    form.order_after(email='zip_code')
    form.order_after(facebook_url='fax_number')
    form.order_after(twitter_url='facebook_url')
    form.order_after(youtube_url='twitter_url')
    form.order_after(instagram_url='youtube_url')
    form.order_after(linkedin_url='instagram_url')
    form.order_after(newsletter_url='linkedin_url')
