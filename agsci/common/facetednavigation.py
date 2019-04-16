from eea.facetednavigation.criteria.handler import Criteria as _Criteria
from eea.facetednavigation.criteria.interfaces import ICriteria
from zope.interface import implementer
from eea.facetednavigation.widgets.storage import Criterion
from eea.facetednavigation.config import ANNO_CRITERIA
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from eea.facetednavigation.settings.interfaces import IDontInheritConfiguration
from zope.globalrequest import getRequest
from Products.CMFCore.utils import getToolByName

from .content.degrees import IDegree
from .indexer import degree_index_field

@implementer(ICriteria)
class DegreeContainerCriteria(_Criteria):

    def idx(self, f):
        return {
            'interest_area' : 'DegreeInterestArea',
            'career' : 'DegreeCareer',
            'employer' : 'DegreeEmployer',
            'club' : 'DegreeClub',
            'facility' : 'DegreeFacility',
            'scholarship' : 'DegreeScholarship',
        }.get(f, f)

    def getFields(self):

        fields = [x[1] for x in degree_index_field]
        
        def sort_order(x):
            try:
                return fields.index(x)
            except ValueError:
                return 99999

        sorted_fields = sorted(IDegree.namesAndDescriptions(), key=lambda x: sort_order(x[0]))

        for (key, field) in sorted_fields:

            if key in fields:

                # Set the cid to the key, minus underscores.
                cid = key
                cid = cid.replace('_', '')

                # Get the vocabulary name
                try:
                    value_type = field.value_type
                except AttributeError:
                    vocabulary_name = ""
                    catalog = "portal_catalog"
                else:
                    vocabulary_name = value_type.vocabularyName
                    catalog = ""

                # Title is the field title
                title = field.title

                yield Criterion(
                    _cid_=cid,
                    widget="checkbox",
                    title=title,
                    index=self.idx(key),
                    operator="or",
                    operator_visible=False,
                    vocabulary=vocabulary_name,
                    position="right",
                    section="default",
                    hidden=False,
                    count=True,
                    catalog=catalog,
                    sortcountable=False,
                    hidezerocount=False,
                    maxitems=50,
                    sortreversed=False,
                )

    @property
    def request(self):
        return getRequest()

    # Caching call for criteria on request, so we don't have to recalculate
    # each time.
    def _criteria(self):
        cache = IAnnotations(self.request)
        key = 'eea.facetednav.%s' % self.context.UID()

        if not cache.has_key(key):
            cache[key] = self.__criteria()

        return cache[key]

    def __criteria(self):
        return PersistentList(self.getFields())

