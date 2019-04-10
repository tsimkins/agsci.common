from bs4 import BeautifulSoup
from zope.component import getAdapter
from zope.component.hooks import getSite

from .interfaces import IBlock

def getParams(_el):
    _ = {}

    for _param in _el.findAll('param'):
        _name = _param.get('name', None)
        _value = _param.get('value', None)
        if _name is not None and _value is not None:
            _[_name] = _value

    return _

def output(self):
    site = getSite()
    _ = self.output_relative_to(site)
    return self.add_blocks(_)

def add_blocks(self, html):

    # Just return value if we're not string or unicode.
    if not isinstance(html, (str, unicode)):
        return html

    # Get the Beautiful Soup object
    soup = BeautifulSoup(html, features="lxml")
    soup.html.hidden = True
    soup.body.hidden = True

    site = getSite()

    found = False

    for _el in soup.findAll('object', attrs={'type' : 'block'}):

        _name = _el.get('name', None)

        if _name:

            try:
                block = getAdapter((site, ), IBlock, _name)
            except:
                pass
            else:

                kwargs = getParams(_el)

                __ = block(_el, **kwargs)

                if __:
                    _el.insert_before(*__)

                _ = _el.extract()

                found = True

    if found:
        return soup.prettify()

    return html