from Acquisition import aq_base
from plone.app.querystring.querybuilder import QueryBuilder as _QueryBuilder
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.batching import Batch

import re

# This querybuilder is a re-worked version that takes into account the
# `order_by_id` and `order_by_title` fields.
class QueryBuilder(_QueryBuilder):

    def id_order(self, ids=[], item=None):
        _id = None

        if item:
            if hasattr(item, 'getId'):
                if hasattr(item.getId, '__call__'):
                    _id = item.getId()
                else:
                    _id = item.getId

            try:
                return ids.index(_id)
            except:
                pass

        return 99999

    def title_order(self, ids=[], item=None):

        _id = None

        if item:
            if hasattr(item, 'Title'):
                if hasattr(item.getId, '__call__'):
                    _id = item.Title()
                else:
                    _id = item.Title

            if _id:

                for (c,_re) in enumerate(ids):
                    if _re.search(_id):
                        return c

        return 99999

    def __call__(self, query, batch=False, b_start=0, b_size=30,
                 sort_on=None, sort_order=None, limit=0, brains=False,
                 custom_query=None):

        order_by_id = self.order_by_id
        order_by_title = self.order_by_title

        _batch = batch
        _sort = False

        if order_by_id or order_by_title:
            batch = False
            _sort = True

        # Get default results
        results = super(QueryBuilder, self).__call__(
            query, batch=batch, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order, limit=limit,
            brains=brains, custom_query=custom_query
        )

        if _sort:

            if order_by_id:
                results = sorted(
                    results,
                    key=lambda x: self.id_order(order_by_id, x),
                )

            elif order_by_title:

                # precompiling regexes
                order_by_title = [
                    re.compile(x)
                    for x in order_by_title
                ]

                results = sorted(
                    results,
                    key=lambda x: self.title_order(order_by_title, x),
                )

            if _batch:
                return Batch(results, b_size, start=b_start)

        return results

    @property
    def order_by_id(self):
        return getattr(aq_base(self.context), 'order_by_id', None)

    @property
    def order_by_title(self):
        return getattr(aq_base(self.context), 'order_by_title', None)