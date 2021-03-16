from plone.app.widgets.base import TextareaWidget

def textarea_autocomplete(self, pattern, pattern_options={}, name=None, value=None):

    super(TextareaWidget, self).__init__('textarea', pattern,
                                            pattern_options)
    self.el.text = ''

    # Added autocomplete=off
    self.el.set('autocomplete', 'off')

    if name is not None:
        self.name = name
    if value is not None:
        self.value = value