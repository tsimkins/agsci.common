from eea.facetednavigation.criteria.handler import Criteria as _Criteria
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.widgets.storage import Criterion
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
from zope.interface import implementer

from ..content.degrees import IDegree
from ..indexer import degree_index_field

@implementer(ICriteria)
class DegreeContainerCriteria(_Criteria):

    def idx(self, f):
        return {
            'interest_area' : 'DegreeInterestArea',
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
                    widget="checkbox_degree_explorer",
                    title=title,
                    index=self.idx(key),
                    operator="or",
                    operator_visible=False,
                    vocabulary=vocabulary_name,
                    position="left",
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

        if key not in cache:
            cache[key] = self.__criteria()

        return cache[key]

    def __criteria(self):

        criteria = [
            Criterion(
                widget="criteria_degree_explorer",
                title="Active Filters",
                position="center",
                section="default",
                hidden=False,
            ),
        ]

        criteria.extend(self.getFields())

        return PersistentList(criteria)
