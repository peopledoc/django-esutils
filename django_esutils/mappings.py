"""Base mapping module for easier specific usage."""
from django.conf import settings

from elasticsearch.exceptions import NotFoundError

from elasticutils.contrib.django import S as _S
from elasticutils.contrib.django import MappingType
from elasticutils.contrib.django import Indexable

from django_esutils import tasks


class S(_S):

    def process_query_fuzzy(self, key, val, action):
        # val here is a (value, min_similarity) tuple
        if isinstance(val, list) or isinstance(val, tuple):
            return {
                'fuzzy': {
                    key: {
                        'value': val[0],
                        'fuzziness': val[1]
                    }
                }
            }
        else:
            return {
                'fuzzy': {
                    key: val
                }
            }

    def all(self):
        for r in self.execute():
            yield r.get_object()


class SearchMappingType(MappingType, Indexable):
    """Base class that implements MappingType and Indexable Elasticutils class
    plus some helpers:

        - compute mapping type name according model name
        - extract document 'magically' according mapping and model fields

    """

    id_field = 'id'
    _nested_fields = None
    _object_fields = None
    rel_sep = '.'

    @classmethod
    def get_index(cls):
        """Returns default peopleask index name from settings."""
        return settings.ES_INDEX_DEFAULT

    @classmethod
    def get_mapping_type_name(cls):
        """Returns model name by default for mapping type name."""
        return cls.get_model()._meta.model_name

    @classmethod
    def doc_type(cls):
        """Shortcuts for easy es base use."""
        return cls.get_mapping_type_name()

    @classmethod
    def get_field_mapping(cls):
        raise NotImplemented('Implement this to speficy the fields to map.')

    @classmethod
    def get_nested_fields(cls, field=None):
        """Returns nested fields of a field or all the nested fields dict.

        ..code-block: python

            >>> ArticleMappingType.get_nested_fields()
            {
                'category': ['pk', 'name']
            }

            >>> ArticleMappingType.get_nested_fields(field=category)
            ['pk', 'name']

        :param field: request only nested fields of this field (optional)
        """
        # not set already
        if cls._nested_fields is None:
            cls._nested_fields = {}
            for k, v in cls.get_field_mapping().items():
                if not v.get('type') == 'nested':
                    continue
                cls._nested_fields[k] = v.get('properties', {}).keys()

        # returns nested fields of a field if field param is passed or all the
        # nested fields dict.
        return cls._nested_fields[field] if field in cls._nested_fields \
            else cls._nested_fields

    @classmethod
    def get_object_fields(cls, field=None):
        # not set already
        if cls._object_fields is None:
            cls._object_fields = {}
            for k, v in cls.get_field_mapping().items():
                if not v.get('type') == 'object':
                    continue
                cls._object_fields[k] = v.get('properties', {}).keys()

        # returns object fields of a field if field param is passed or all the
        # nested fields dict.
        return cls._object_fields[field] if field in cls._object_fields \
            else cls._object_fields

    @classmethod
    def get_mapping(cls):
        """Returns ES mapping spec including get_field_mapping result."""
        return {
            '_all': {
                'enabled': settings.ES_SOURCE_ENABLED,
            },
            '_source': {
                'enabled': settings.ES_SOURCE_ENABLED,
            },
            'properties': cls.get_field_mapping(),
        }

    @classmethod
    def flat(cls, field, queryset, column='pk', order_by=None):
        """Flats queryset values accoding passed column.

        :params relate_name: name of the field related.
        :params queryset: related queryset.
        :params column: default=pk.
        :params order_by: default=column.
        """

        qs = queryset.values(*cls.get_nested_fields(field=field))
        qs = qs.order_by(order_by or column)
        return list(qs)

    @classmethod
    def get_object_by_id(cls, obj_id):
        kwargs = {cls.id_field: obj_id}
        return cls.get_model().objects.get(**kwargs)

    @classmethod
    def serialize_field(cls, obj, k):
        # split key if is a 2 level key or one level key, ex.:
        #   - 'id', None if k == 'id'
        #   - 'author', 'first_name' if k == 'author.first_name'
        k_1, k_2 = (k, None) if cls.rel_sep not in k \
            else k.split(cls.rel_sep)

        # update the doc according splitted key, ex.: {
        #     'id': obj.id,
        # }
        # ... or if is a 2 level key: {
        #     'author.first_name': obj.author.first_name,
        # }
        field = getattr(obj, k_1, None)
        if field and k_2:
            field = getattr(field, k_2, None)

        return k_1, field

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """Returns json doc to index for a given pkand the current mapping."""

        # retrieve object if not passed
        if obj is None:
            obj = cls.get_object_by_id(obj_id)

        # shortcut
        mapping_keys = [cls.id_field] + cls.get_field_mapping().keys()

        # build doc according mapping keys and obj values
        doc = {}
        for k in mapping_keys:
            model_k, doc[k] = cls.serialize_field(obj, k)

            # ensure pk serialization
            if doc[k] and k == cls.id_field:
                doc[k] = str(doc[k])

            if doc[k].__class__.__name__ in ['ManyRelatedManager',
                                             'RelatedManager']:
                doc[k] = cls.flat(k, doc[k])
                continue

            if model_k in obj._meta.get_all_field_names() and doc[k]:
                field_type = obj._meta.get_field(model_k).get_internal_type()

                if field_type == 'ForeignKey' and \
                   'properties' in cls.get_field_mapping()[k]:
                    foreign_obj = doc[k]
                    doc[k] = {}

                    for k_field in cls.get_field_mapping()[k]['properties']:
                        k_1, doc[k][k_field] = cls.serialize_field(foreign_obj, k_field)  # noqa

        return doc

    @classmethod
    def search(cls):
        return S(cls)

    @classmethod
    def count(cls):
        return cls.search().count()

    @classmethod
    def query(cls, **kwargs):
        return cls.search().query(**kwargs)

    @classmethod
    def generate_mappings(cls):
        return dict([(doc_type, {
        }) for doc_type in settings.ES_DOC_TYPES])

    @classmethod
    def create_index(cls, es=None, index=None, mappings=None):

        # ensure es and index values
        es = es or cls.get_es()
        index = index or cls.get_index()

        if not es.indices.exists(index):
            # passed or default mappings
            mappings = mappings or cls.generate_mappings()
            # do create
            es.indices.create(index, body={
                'settings': settings.ES_INDEX_SETTINGS,
                'mappings': mappings,
            })

    @classmethod
    def update_mapping(cls, es=None, index=None, doc_type=None, mapping=None,
                       delete_previous_mapping=True):
        """Creates index with current mapping if not exist yet."""
        # ensure es and index values
        es = es or cls.get_es()
        index = index or cls.get_index()
        doc_type = doc_type or cls.doc_type()
        mapping = mapping or cls.get_mapping()

        # create index if not exist yet
        cls.create_index(es=es, index=index)

        # delete previous mapping if specified
        if delete_previous_mapping:
            try:
                es.indices.delete_mapping(index, doc_type)
            except NotFoundError:
                pass

        # update mapping if needed
        es.indices.put_mapping(doc_type, {
            doc_type: mapping
        }, index=index)

    @classmethod
    def run_index(cls, ids):
        if not ids:
            return
        tasks.index_objects.delay(cls, ids)

    @classmethod
    def run_index_all(cls):
        cls.run_index(list(cls.get_model().objects.values_list(cls.id_field,
                                                               flat=True)))

    @classmethod
    def run_unindex(cls, ids):
        if not ids:
            return
        tasks.unindex_objects.delay(cls, ids)

    @classmethod
    def on_post_save(cls, sender, instance, **kwargs):
        """Indexes passed object when call from a model post_save signal.
        """
        cls.run_index([getattr(instance, cls.id_field)])

    @classmethod
    def on_post_update(cls, sender, queryset, **kwargs):
        """Indexes passed object when call from a model post_save signal.
        """
        cls.run_index(list(queryset.values_list(cls.id_field, flat=True)))

    @classmethod
    def on_post_delete(cls, sender, instance, **kwargs):
        """Unindexes passed object when call from a model post_delete signal.
        """
        cls.run_unindex([getattr(instance, cls.id_field)])
