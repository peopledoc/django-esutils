# -*- coding: utf-8 -*-
from elasticutils import F

from rest_framework.filters import SearchFilter


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
                 default_action='', all_filter='q', prefix_fields=None):

        self.search_fields = search_fields or []
        self.search_actions = search_actions or {}
        self.search_terms = search_terms or {}
        self.all_filter = all_filter
        self.prefix_fields = prefix_fields or []

        self.mapping_type = mapping_type
        self.nested_fields = self.mapping_type.get_nested_fields()
        self.object_fields = self.mapping_type.get_object_fields()

        self.raw_fields = [self.all_filter, 'ids'] + self.nested_fields.keys()
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
        # Action must be either None or one that can be handled by Elasticutils
        # According to Elasticutils
        # Available actions are : startswith, prefix, in, range and distance
        action = self.search_actions.get(f, self.default_action)

        if not action and f in self.prefix_fields:
            action = 'prefix'

        field_action = '{0}__{1}'.format(f, action) if action else f

        # If term is an empty string, we are looking for a missing relation
        if term == '':
            term = None
        return F(**{field_action: term})

    def _get_filter_nested_item(self, f, term, action='or'):

        # The following is the research for missing nested relations
        # Like looking for a library (object) that has no books (nested)
        if not term or term == '':
            return {
                'not': {
                    'nested': {
                        'path': f,
                        'filter': {
                            'match_all': {}
                        }
                    }
                }
            }

        fields = list(self.nested_fields.get(f))

        is_int = True
        try:
            int(term)
        except:
            is_int = False

        if not is_int:
            mapping_fields = self.mapping_type.get_field_mapping()
            for nf in fields:
                if mapping_fields[f]['properties'][nf]['type'] == 'integer':
                    fields.remove(nf)

        return {
            'nested': {
                'path': f,
                'filter': {
                    action: [_F(f, nf, term) for nf in fields]
                }
            }
        }

    def get_filter_nested(self, f, terms):
        if terms:
            return [self._get_filter_nested_item(f, t) for t in terms]  # noqa

        return [self._get_filter_nested_item(f, terms)]

    def get_filter_ids(self, values):
        return {
            'ids': {
                'values': [int(i) for i in values]
            }
        }

    def get_filter_all(self, value):
        return {
            'or': [
                {
                    'term': {
                        '_all': value.lower()
                    }
                },
                {
                    'prefix': {
                        '_all': value.lower()
                    }
                }
            ]
        }

    def build_complete_filter_raw(self, search, filter_raw):
        filters = {}
        if 'filter' in search:
            current = search['filter']
            if 'and' in current:
                filters = current
            else:
                filters['and'] = [current, ]
            filters['and'].append(filter_raw)
        else:
            filters = filter_raw
        return filters

    def update_query(self, query, f, term=None, raw=False):
        if not raw and f not in self.raw_fields:
            return query.filter(self.get_filter(f, term))

        elif raw and f in self.nested_fields:
            for f_raw in self.get_filter_nested(f, term):
                filters = self.build_complete_filter_raw(
                    query.build_search(),
                    f_raw)
                query = query.filter_raw(filters)

        elif raw and f == 'ids':
            filters = self.build_complete_filter_raw(
                query.build_search(),
                self.get_filter_ids(term))
            query = query.filter_raw(filters)

        elif raw and f == self.all_filter:
            filters = self.build_complete_filter_raw(
                query.build_search(),
                self.get_filter_all(term))
            query = query.filter_raw(filters)
        return query

    @property
    def qs(self):
        query = self.queryset

        if query is None:
            query = self.mapping_type.query()

        for f in self.search_fields:
            if f not in self.search_terms.keys():
                continue

            term = self.search_terms.get(f)
            query = self.update_query(query, f, term)

        for f in self.raw_fields:
            if f not in self.search_terms.keys():
                continue

            term = self.search_terms.get(f)

            query = self.update_query(query, f, term, raw=True)

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
        all_filter = getattr(view, 'all_filter', 'q')
        mapping_type = getattr(view, 'mapping_type', None)
        object_fields = mapping_type.get_object_fields()

        if all_filter not in search_keys:
            search_keys.append(all_filter)

        if 'ids' not in search_keys:
            search_keys.append('ids')

        # For object type, you can filter on anny inner relation
        # this code appends the inner relations to your search keys
        for key, fields in object_fields.items():
            for f in fields:
                s_key = '{0}.{1}'.format(key, f)
                if s_key not in search_keys:
                    search_keys.append(s_key)

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
            # A value can be None and found in the query params
            # which means we search for the missing fields
            value = None
            found = False
            # get value or valuelist
            for key in params.keys():
                # ex.: {'tag': 'yo'}
                if key == s_key:
                    found = True
                    value = params.get(key)
                    break
                # ex.: {'tags[]': [1, 2]}
                if key == '{0}[]'.format(s_key):
                    found = True
                    value = params.getlist(key)
                    break
            # nothing to search
            if not value and not found:
                continue
            # update search values

            search_terms[s_key] = value

        return search_terms

    def filter_queryset(self, request, queryset, view):

        search_terms = self.get_search_terms(request, view, queryset)
        search_actions = getattr(view, 'search_actions', None)

        search_fields = getattr(view, 'search_fields', search_terms.keys())
        all_filter = getattr(view, 'all_filter', 'q')
        prefix_fields = getattr(view, 'prefix_fields', None)

        mapping_type = getattr(view, 'mapping_type', None)

        filter_class = self.get_filter_class(view, queryset)

        return filter_class(search_fields=search_fields,
                            search_actions=search_actions,
                            search_terms=search_terms,
                            mapping_type=mapping_type,
                            queryset=queryset,
                            all_filter=all_filter,
                            prefix_fields=prefix_fields).qs
