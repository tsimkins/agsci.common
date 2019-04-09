from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from plone.app.textfield.interfaces import ITransformer, TransformError
from plone.app.textfield.transform import LOG
from plone.app.textfield.transform import PortalTransformsTransformer as _PortalTransformsTransformer
from zope.component.hooks import getSite
from zope.interface import implementer

@implementer(ITransformer)
class PortalTransformsTransformer(_PortalTransformsTransformer):

    def __call__(self, value, mimeType):
        # shortcut it we have no data
        if value.raw is None:
            return u''

        # shortcut if we already have the right value
        if mimeType is value.mimeType:
            return value.output

        site = getSite()

        transforms = getToolByName(site, 'portal_transforms', None)

        if transforms is None:
            raise TransformError("Cannot find portal_transforms tool")

        # Expand blocks if we're HTML
        source_value = value.raw_encoded

        if hasattr(value, 'add_blocks') and value.mimeType in (
            'text/x-html-safe',
            'text/html'
        ):

            source_value = value.add_blocks(source_value)

        try:
            data = transforms.convertTo(mimeType,
                                        source_value,
                                        mimetype=value.mimeType,
                                        context=self.context,
                                        # portal_transforms caches on this
                                        object=value._raw_holder,
                                        encoding=value.encoding)
            if data is None:
                # TODO: i18n
                msg = (u'No transform path found from "%s" to "%s".' %
                       (value.mimeType, mimeType))
                LOG.error(msg)
                # TODO: memoize?
                # plone_utils = getToolByName(self.context, 'plone_utils')
                # plone_utils.addPortalMessage(msg, type='error')
                # FIXME: message not always rendered, or rendered later on
                # other page.
                # The following might work better, but how to get the request?
                # IStatusMessage(request).add(msg, type='error')
                return u''

            else:
                output = data.getData()
                return output.decode(value.encoding)
        except ConflictError:
            raise
        except Exception as e:
            # log the traceback of the original exception
            LOG.error("Transform exception", exc_info=True)
            raise TransformError('Error during transformation', e)