# -*- coding: utf-8 -*-
from elasticutils import F
from elasticutils.contrib.django import S as _S

from rest_framework.filters import SearchFilter


class S(_S):

    def all(self):
        for r in self.execute():
            yield r.get_object()


def _F(path, field, term, action='term'):
    """Returns F with path:field for nested filtering.

    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-nested-filter.html  # noqa
    """
    return {
        action: {
            '{0}.{1}'.format(path, field): term
        }
    }


class ElasticutilsFilterSet(object):

    def __init__(self, search_fields=None, search_actions=None,
                 search_terms=None, mapping_type=None, queryset=None,
                 default_action=''):

        self.search_fields = search_fields or []
        self.search_actions = search_actions or {}
        self.search_terms = search_terms or {}

        self.mapping_type = mapping_type
        self.nested_fields = self.mapping_type.get_nested_fields()
        self.queryset = queryset

        self.default_action = default_action

    def __iter__(self):
        for obj in self.qs:
            yield obj

    def __len__(self):
        return self.count()

    def __getitem__(self, key):
        return self.qs[key]

    def get_filter(self, f, term):
        action = self.search_actions.get(f, self.default_action)
        field_action = '{0}__{1}'.format(f, action) if action else f
        return F(**{field_action: term})

    def _get_filter_nested_item(self, f, term):

        fields = self.nested_fields.get(f)

        return {
            'nested': {
                'path': f,
                'filter': {
                    'or': [_F(f, nf, term) for nf in fields]
                }
            }
        }

    def get_filter_nested(self, f, terms):
        return [self._get_filter_nested_item(f, t) for t in terms if t != '']

    def get_filter_ids(self, values):
        return {
            'ids': {
                'values': [int(i) for i in values]
            }
        }

    @property
    def qs(self):

        query = self.queryset or self.mapping_type.query()

        for f in self.search_fields:
            term = self.search_terms.get(f)
            # nothing to filter on
            if not term:
                continue
            if f == 'ids':
                import ipdb; ipdb.set_trace()
                query = query.filter_raw(self.get_filter_ids(term))
            if f not in self.nested_fields:
                query = query.filter(self.get_filter(f, term))
                continue
            for f_raw in self.get_filter_nested(f, term):
                query = query.filter_raw(f_raw)

        return query

    @property
    def count(self):
        return self.qs.count()

    @property
    def form(self):
        raise NotImplemented('Form not yet implemented')

    def get_ordering_field(self):
        raise NotImplemented('Form not yet implemented')

    @property
    def ordering_field(self):
        if not hasattr(self, '_ordering_field'):
            self._ordering_field = self.get_ordering_field()
        return self._ordering_field

    def get_order_by(self, order_choice):
        return [order_choice]

    @classmethod
    def filter_for_field(cls, f, name):
        raise NotImplemented('Form not yet implemented')

    @classmethod
    def filter_for_reverse_field(cls, f, name):
        raise NotImplemented('Form not yet implemented')


class ElasticutilsFilterBackend(SearchFilter):

    key_separator = ':'
    query_splitter = ' '

    def get_filter_class(self, view, queryset=None):
        return getattr(view, 'filter_class', ElasticutilsFilterSet)

    def get_search_keys(self, view, queryset=None):
        search_keys = getattr(view, 'search_fields', [])
        if 'q' not in search_keys:
            search_keys.append('q')
        if 'ids' not in search_keys:
            search_keys.append('ids')
        return search_keys

    def split_query_str(self, query_str):
        """
        >>> self.split_query_str('helo')
        {'_all': 'helo'}

        >>> self.split_query_str('firstname:bob lastname:dylan')
        {'firstname': 'bob', 'lastname': 'dylan'}
        """
        # little cleaning
        query_str = query_str.strip()

        if self.key_separator not in query_str:
            return {'_all': query_str}

        return dict([s.strip().split(self.key_separator)
                     for s in query_str.split(self.query_splitter)])

    def get_search_terms(self, request, view, queryset=None):
        """Return Splitted query string automagically.
        """
        params = request.QUERY_PARAMS.copy()
        search_keys = self.get_search_keys(view)

        search_terms = dict()

        for s_key in search_keys:
            # no value found at start
            value = None
            # get value or valuelist
            for key in params.keys():
                # ex.: {'tag': 'yo'}
                if key == s_key:
                    value = params.get(key)
                    break
                # ex.: {'tags[]': [1, 2]}
                if key == '{0}[]'.format(s_key):
                    value = params.getlist(key)
                    break
            # nothing to search
            if not value:
                continue
            # update search values
            search_terms[s_key] = value
        return search_terms

    def filter_queryset(self, request, queryset, view):

        search_terms = self.get_search_terms(request, view, queryset)
        search_actions = getattr(view, 'search_actions', None)
        search_fields = getattr(view, 'search_fields', search_terms.keys())

        mapping_type = getattr(view, 'mapping_type', None)

        filter_class = self.get_filter_class(view, queryset)

        return filter_class(search_fields=search_fields,
                            search_actions=search_actions,
                            search_terms=search_terms,
                            mapping_type=mapping_type,
                            queryset=queryset).qs
