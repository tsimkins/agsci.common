from plone.app.event import base
from plone.event.interfaces import IEventAccessor
from plone.event.utils import date_to_datetime
from plone.event.utils import is_date
from plone.event.utils import is_datetime
from plone.event.utils import utc
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import datetime
import icalendar
import random
import six
import transaction


def ical_import(container, ics_resource, event_type,
                sync_strategy=base.SYNC_KEEP_NEWER):
    cal = icalendar.Calendar.from_ical(ics_resource)
    events = cal.walk('VEVENT')

    cat = getToolByName(container, 'portal_catalog')
    container_path = '/'.join(container.getPhysicalPath())

    def _get_by_sync_uid(uid):
        return cat(
            sync_uid=uid,
            path={'query': container_path, 'depth': 1}
        )

    def _get_prop(prop, item, default=None):
        ret = default
        if prop in item:
            ret = safe_unicode(item.decoded(prop))
        return ret

    def _from_list(ical, prop):
        """For EXDATE and RDATE recurrence component properties, the dates can
        be defined within one EXDATE/RDATE line or for each date an individual
        line.
        In the latter case, icalendar creates a list.
        This method handles this case.

        TODO: component property parameters like TZID are not used here.
        """
        val = ical[prop] if prop in ical else []
        if not isinstance(val, list):
            val = [val]

        # Zip multiple lines into one, since jquery.recurrenceinput.js does
        # not support multiple lines here
        # https://github.com/collective/jquery.recurrenceinput.js/issues/15
        ret = ''
        for item in val:
            ret = '%s,' % ret if ret else ret  # insert linebreak
            ical_val = item.to_ical()
            if six.PY3 and isinstance(ical_val, six.binary_type):
                ical_val = ical_val.decode('utf8')
            ret = '%s%s' % (ret, ical_val)
        return '%s:%s' % (prop, ret) if ret else None

    count = 0
    for item in events:
        start = _get_prop('DTSTART', item)
        end = _get_prop('DTEND', item)
        if not end:
            duration = _get_prop('DURATION', item)
            if duration:
                end = start + duration
            # else: whole day or open end

        whole_day = False
        open_end = False
        if is_date(start) and (is_date(end) or end is None):
            # All day / whole day events
            # End must be same type as start (RFC5545, 3.8.2.2)
            whole_day = True
            if end is None:
                end = start
            if start < end:
                # RFC5545 doesn't define clearly, if all day events should have
                # a end date one day after the start day at 0:00.
                # Internally, we handle all day events with start=0:00,
                # end=:23:59:59, so we substract one day here.
                end = end - datetime.timedelta(days=1)
            start = base.dt_start_of_day(date_to_datetime(start))
            end = base.dt_end_of_day(date_to_datetime(end))
        elif is_datetime(start) and end is None:
            # Open end event, see RFC 5545, 3.6.1
            open_end = True
            end = base.dt_end_of_day(date_to_datetime(start))
        assert(is_datetime(start))
        assert(is_datetime(end))

        # Set timezone, if not already set
        tz = base.default_timezone(container, as_tzinfo=True)
        if not getattr(start, 'tzinfo', False):
            start = tz.localize(start)
        if not getattr(end, 'tzinfo', False):
            end = tz.localize(end)

        title = _get_prop('SUMMARY', item)
        description = _get_prop('DESCRIPTION', item)
        location = _get_prop('LOCATION', item)

        if not location:
            location = "Virtual"

        url = _get_prop('URL', item)

        rrule = _get_prop('RRULE', item)
        rrule = rrule.to_ical() if rrule else ''
        if rrule:
            if six.PY3 and isinstance(rrule, six.binary_type):
                rrule = rrule.decode('utf8')
            rrule = 'RRULE:%s' % rrule
        rdates = _from_list(item, 'RDATE')
        exdates = _from_list(item, 'EXDATE')
        rrule = '\n'.join([it for it in [rrule, rdates, exdates] if it])

        # TODO: attendee-lists are not decoded properly and contain only
        # vCalAddress values
        attendees = item.get('ATTENDEE', ())

        contact = _get_prop('CONTACT', item)
        categories = item.get('CATEGORIES', ())

        if getattr(categories, 'cats', False):
            categories = tuple([safe_unicode(it.strip()) for it in categories.cats])

        else:
            categories = []

        ext_modified = utc(_get_prop('LAST-MODIFIED', item))

        content = None
        new_content_id = None
        existing_event = None
        sync_uid = _get_prop('UID', item)
        if sync_uid and sync_strategy is not base.SYNC_NONE:
            existing_event = _get_by_sync_uid(sync_uid)
        if existing_event:
            if sync_strategy == base.SYNC_KEEP_MINE:
                # On conflict, keep mine
                continue

            exist_event = existing_event[0].getObject()
            acc = IEventAccessor(exist_event)

            if sync_strategy == base.SYNC_KEEP_NEWER and\
                    (not ext_modified or acc.last_modified > ext_modified):
                # Update only if modified date was passed in and it is not
                # older than the current modified date.  The client is not
                # expected to update the "last-modified" property, it is the
                # job of the server (calendar store) to keep it up to date.
                # This makes sure the client did the change on an up-to-date
                # version of the object.  See
                # http://tools.ietf.org/search/rfc5545#section-3.8.7.3
                continue

            # Else: update
            content = exist_event
        else:
            new_content_id = str(random.randint(0, 99999999))
            container.invokeFactory(event_type,
                                    id=new_content_id,
                                    title=title,
                                    description=description)
            content = container[new_content_id]

        assert(content)  # At this point, a content must be available.

        event = IEventAccessor(content)
        event.title = title
        event.description = description
        event.start = start
        event.end = end
        event.whole_day = whole_day
        event.open_end = open_end
        event.location = location
        event.event_url = url
        event.recurrence = rrule
        event.attendees = attendees
        event.contact_name = contact
        event.public_tags = categories

        if url:
            content.setLayout('event_redirect_view')

        if sync_uid and sync_strategy is not base.SYNC_NONE:
            # Set the external sync_uid for sync strategies other than
            # SYNC_NONE.
            event.sync_uid = sync_uid
        notify(ObjectModifiedEvent(content))

        # Use commits instead of savepoints to avoid "FileStorageError:
        # description too long" on large imports.
        transaction.get().commit()  # Commit before rename

        if new_content_id and new_content_id in container:
            # Rename with new id from title, if processForm didn't do it.
            chooser = INameChooser(container)
            new_id = chooser.chooseName(title, content)
            content.aq_parent.manage_renameObject(new_content_id, new_id)

        # Do this at the end, otherwise it's overwritten
        if ext_modified:
            event.last_modified = ext_modified

        count += 1

    return {'count': count}
