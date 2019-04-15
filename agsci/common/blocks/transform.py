from plone.app.textfield.value import RichTextValue

class BlockTransformer(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, value, mimeType):

        # If we have a value, run the 'apply_blocks' method.
        if value.raw:

            if hasattr(value, 'add_blocks') and value.mimeType in (
                'text/x-html-safe',
                'text/html'
            ):

                # Expand blocks if we're HTML
                source_value = value.raw_encoded

                source_value = value.add_blocks(source_value)

                value = RichTextValue(
                    raw=source_value,
                    mimeType=value.mimeType,
                    outputMimeType=value.outputMimeType,
                )

        # Return the output of the next adapter in the chain
        return self.context(value, mimeType)