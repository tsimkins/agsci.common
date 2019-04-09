from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from zope.component.hooks import getSite

class BaseBlock(object):

    template_base = '++resource++agsci.common.blocks/'
    template = 'base.j2'

    defaults = {}

    @property
    def site(self):
        return getSite()

    def __init__(self, context):
        self.context = context
    
    def __call__(self, el, **kwargs):
        rendered = self.render(el, **kwargs)
        soup = BeautifulSoup(rendered, features="lxml")
        soup.html.hidden = True
        soup.body.hidden = True
        return soup

    def render(self, el, **kwargs):
        resource = self.site.restrictedTraverse(self.template_base)

        loader = FileSystemLoader(resource.context.path)
        
        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template(
            self.template
        )

        defaults = dict(self.defaults)

        defaults.update(kwargs)

        return template.render(html=el.encode_contents(), **defaults)

class StatBlock(BaseBlock):
    template = 'stat.j2'
    
    defaults = {
        'align' : 'left'
    }