from eea.facetednavigation.widgets.checkbox.widget import Widget as _Widget
from eea.facetednavigation.widgets import ViewPageTemplateFile

class Widget(_Widget):

    widget_type = 'checkbox_degree_explorer'
    index = ViewPageTemplateFile('widget.pt')