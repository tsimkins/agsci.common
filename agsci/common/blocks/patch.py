from bs4 import BeautifulSoup
from zope.component import getAdapter
from zope.component.hooks import getSite

from .interfaces import IBlock

def output(self):
    site = getSite()
    _ = self.output_relative_to(site)
    return self.add_blocks(_)

def add_blocks(self, html):

    # Get the Beautiful Soup object
    soup = BeautifulSoup(html, features="lxml")
    soup.html.hidden = True
    soup.body.hidden = True

    site = getSite()

    found = False

    for _el in soup.findAll('aside'):

        kwargs = dict([(k.replace('data-', '', 1), v) for (k,v) in _el.attrs.iteritems() if k.startswith('data-')])

        _name = kwargs.get('name', None)

        if _name:

            try:
                block = getAdapter((site, ), IBlock, _name)
            except:
                pass
            else:
                __ = block(_el, **kwargs)

                if __:
                    _el.insert_before(*__)

                _ = _el.extract()

                found = True

    if found:
        return soup.prettify()

    return html