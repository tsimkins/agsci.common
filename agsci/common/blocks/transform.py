from bs4 import BeautifulSoup
from plone.app.textfield.value import RichTextValue
from zope.component import getAdapter

from .interfaces import IBlock

class BlockTransformer(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, value, mimeType):

        # If we have a value, run the 'apply_blocks' method.
        if value.raw:

            if value.mimeType in (
                'text/x-html-safe',
                'text/html'
            ):

                # Expand blocks if we're HTML
                source_value = self.add_blocks(value.raw)

                value = RichTextValue(
                    raw=source_value,
                    mimeType=value.mimeType,
                    outputMimeType=value.outputMimeType,
                )

        # Return the output of the next adapter in the chain
        return self.context(value, mimeType)

    def get_params(self, _el):
        _ = {}

        for _param in _el.findAll('param'):
            _name = _param.get('name', None)
            _value = _param.get('value', None)
            if _name is not None and _value is not None:
                _[_name] = _value

        return _

    def add_blocks(self, html):

        # Just return value if we're not string or unicode.
        if not isinstance(html, (str, unicode)):
            return html

        # Get the Beautiful Soup object
        soup = BeautifulSoup(html, features="lxml")
        soup.html.hidden = True
        soup.body.hidden = True

        found = False

        for _el in soup.findAll('object', attrs={'type' : 'block'}):

            _name = _el.get('name', None)

            if _name:

                try:
                    block = getAdapter((self.context, ), IBlock, _name)
                except:
                    pass
                else:

                    kwargs = self.get_params(_el)

                    __ = block(_el, **kwargs)

                    if __:
                        parent = _el.parent

                        # If the object is the only thing inside the parent.
                        if parent.name in ('p',) and len(parent.contents) == 1:
                            parent.insert_before(*__)
                            _ = parent.extract()
                        else:
                            _el.insert_before(*__)

                    _ = _el.extract()

                    found = True

        if found:
            return soup.prettify()

        return html