from bs4 import BeautifulSoup
from plone.app.textfield.value import RichTextValue
from zope.component import getAdapter

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from ..constants import RESOLVEUID_RE

from .interfaces import IBlock
from . import InlineItemsBlock

class BlockTransformer(object):

    iframe_domains = [
        'calendar.google.com',
        'maps.google.com',
        'player.vimeo.com',
        'www.google.com',
        'www.youtube.com',
        'youtube.com',
        'psu.mediaspace.kaltura.com',
        'cdnapisec.kaltura.com',
        'videoplayer.telvue.com',
        'app.powerbi.com',
    ]

    iframe_classes = {
        'calendar.google.com' : 'aspect-4-3',
        'maps.google.com' : 'aspect-3-2',
        'www.google.com' : 'aspect-3-2',
        'psu.mediaspace.kaltura.com' : 'aspect-kaltura',
        'cdnapisec.kaltura.com' : 'aspect-kaltura',
        'videoplayer.telvue.com' : 'aspect-16-9',
        'app.powerbi.com' : 'aspect-4-3',
    }

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

        # Just return value if we're not string
        if not isinstance(html, str):
            return html

        # Get the Beautiful Soup object
        soup = BeautifulSoup(html, features="lxml")
        soup.html.hidden = True
        soup.body.hidden = True

        found = False

        # Handle 'object' blocks
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

                    undef = _el.extract()

                    found = True

        # Handle special classes of links (card, etc.)

        for _el in soup.findAll('a'):

            _href = _el.get('href', None)
            _class = _el.get('class', None)

            if isinstance(_class, (str, )):
                _class = _class.split()
            elif isinstance(_class, (list, tuple)):
                _class = list(_class)
            else:
                _class = []

            if _href and 'card' in _class:
                m = RESOLVEUID_RE.match(_href)

                if m:
                    uid = m.group(1)

                    if uid:
                        block = InlineItemsBlock(self.context)

                        try:
                            _rendered = block.render(_el, uid=uid)
                        except:
                            pass
                        else:
                            new_a = BeautifulSoup(_rendered, features="lxml").html.body.contents[0]

                            _el.replaceWith(new_a)

                            found = True

        # Handle Youtube iframes
        for _el in soup.findAll('iframe'):

            _src = _el.get('src', None)
            _class = _el.get('class', None)

            if isinstance(_class, str):
                _class = _class.split()
            elif isinstance(_class, (list, tuple)):
                _class = list(_class)
            else:
                _class = []

            if _src:

                # Get the domain from the iframe source and see if it's one
                # that we want to make responsive
                domain = urlparse(_src).netloc

                if domain and domain in self.iframe_domains or \
                    any([x.startswith('w-') for x in _class]):

                    # Transfer the iframe class to the wrapper

                    # Get default aspect ration class
                    if not _class:
                        iframe_class = self.iframe_classes.get(domain, None)
                        if iframe_class:
                            _class.append(iframe_class)

                    _class.append("youtube-video-embed")

                    # Create a wrapper and set the class
                    wrapper = soup.new_tag(
                        name='div',
                        attrs={
                            'class' : " ".join(_class),
                        },
                    )

                    # Remove the iframe class
                    _el['class'] = []

                    # Remove the iframe's parent if it's a <p> tag
                    parent = _el.parent

                    # If the object is the only thing inside the parent.
                    if parent.name in ('p',) and len(parent.contents) == 1:
                        parent.insert_before(wrapper)
                        parent = parent.extract()
                    else:
                        # Put the wrapper into the DOM before the iframe
                        _el.insert_before(wrapper)

                    # Pull the iframe out of the DOM
                    _el = _el.extract()

                    # Append the iframe to the wrapper
                    wrapper.append(_el)

                    found = True


        if found:
            return str(soup)

        return html
