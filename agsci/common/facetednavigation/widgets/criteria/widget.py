from eea.facetednavigation.widgets.criteria.widget import Widget as _Widget
from eea.facetednavigation.widgets import ViewPageTemplateFile
from plone.i18n.normalizer import urlnormalizer as normalizer

class Widget(_Widget):

    widget_type = 'criteria_degree_explorer'
    #widget_type_css = 'criteria'
    index = ViewPageTemplateFile('widget.pt')

    @property
    def css_class(self):
        """ Widget specific css class
        """
        css_type = self.widget_type #_css
        css_title = normalizer.normalize(self.data.title)
        return 'faceted-{0}-widget section-{1}'.format(css_type, css_title)