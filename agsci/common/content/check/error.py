try:
    from plone.base.utils import safe_text as safe_unicode
except ImportError:
    from Products.CMFPlone.utils import safe_unicode

class Error(object):

    def __init__(self, check='', msg='', data=None):
        self.check = check
        self.msg = msg
        self.data = data

    def klass(self):
        return 'error-check'

    def __repr__(self):
        return safe_unicode(self.msg)

    def render(self):

        if self.check and hasattr(self.check, 'render'):
            return self.check.render

        return False

    def render_action(self):

        if self.check and hasattr(self.check, 'render_action'):
            return self.check.render_action

        return False

    @property
    def error_code(self):
        return self.check.error_code

    @property
    def sort_order(self):
        return self.check.sort_order

class ContentCheckError(Error):
    pass

class ManualCheckError(Error):
    pass
