from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import provider

from agsci.common import AgsciMessageFactory as _

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
class ICollectionFields(model.Schema):

    order_by_id = schema.List(
        title=_(u"Order by id"),
        description=_(u"The content will show items with the listed ids first, and then sort by the default sort order.  One per line."),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    order_by_title = schema.List(
        title=_(u"Order by Title"),
        description=_(u"The content will show items matching the specified regex patterns first, and then sort by the default sort order.  One per line."),
        value_type=schema.TextLine(required=True),
        required=False,
    )

    show_person_areas = schema.Bool(
        title=_(u"Show 'Areas of Expertise' for people in results."),
        description=_(u""),
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

    listing_after_text = schema.Bool(
        title=_(u"Show text after folder contents"),
        description=_(u"This will show the Body Text field after the folder contents instead of before."),
        required=False,
    )

    show_date = schema.Bool(
        title=_(u"Show date"),
        description=_(u"This will show the publication date for each item in the folder listing."),
        required=False,
    )

    show_description = schema.Bool(
        title=_(u"Show description"),
        description=_(u"This will show the description for each item in the folder listing."),
        required=False,
    )

    show_image = schema.Bool(
        title=_(u"Show Lead Image in folder listing"),
        description=_(u"This will show the lead image for each item in the folder listing."),
        required=False,
    )

@provider(IFormFieldProvider)
class IHomepageFields(model.Schema):

    show_homepage_text = schema.Bool(
        title=_(u"Show Homepage Text"),
        description=_(u"Display the text on the homepage."),
        required=False,
    )

    slider_random = schema.Bool(
        title=_(u"Randomize HomePage Slider"),
        description=_(u"Display slider images in a random rather than sequential order."),
        required=False,
    )


@provider(IFormFieldProvider)
class IEventFields(model.Schema):

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


