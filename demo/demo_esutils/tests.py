from datetime import datetime

from django.test import TestCase
from django.utils.timezone import get_current_timezone
from django.utils.timezone import make_aware

from elasticutils import F

from freezegun import freeze_time

from demo_esutils.models import Category
from demo_esutils.models import Article
from demo_esutils.models import User
from demo_esutils.mappings import ArticleMappingType as M
from django_esutils.filters import ElasticutilsFilterSet
from django_esutils.filters import ElasticutilsFilterBackend


class BaseTest(TestCase):
    fixtures = ['test_data']

    def setUp(self):
        self.louise = User.objects.get(pk=2)
        self.florent = User.objects.get(pk=1)
        self. search_fields = ['author.username',
                               'author.email',
                               'category_id',
                               'category.name',
                               'created_at',
                               'subject',
                               'content',
                               'status',
                               'contributors']
        self.mapping_type = M
        M.update_mapping()
        M.run_index_all()
        M.refresh_index()

    def tearDown(self):
        User.objects.all().delete()
        Category.objects.all().delete()
        Article.objects.all().delete()
        M.refresh_index()

    def freezed_time(self, *args):
        return make_aware(datetime(*args), get_current_timezone())


class MappingTestCase(BaseTest):

    def test_index(self):

        # keep previous indexed objec count
        prev_count = M.count()

        # create an article
        category = Category.objects.create(name='The Tests')

        article1 = Article()
        article1.author = self.florent
        article1.category = category
        article1.content = '!'
        article1.subject = 'make it works'

        article2 = Article()
        article2.author = self.louise
        article2.category = category
        article2.content = 'yo'
        article2.subject = 'My amazing article'

        for i, art in enumerate([article1, article2]):
            # save
            art.save()
            # refresh index
            M.refresh_index()
            # check added
            add_count = M.count()
            self.assertEqual(add_count, prev_count + i + 1)

        for i, a in enumerate([article1, article2]):
            # remove an article
            a.delete()
            # refresh index
            M.refresh_index()
            # check removed
            del_count = M.count()
            self.assertEqual(del_count, add_count - i - 1)

    def test_queryset_update(self):
        # update some contents
        self.assertEqual(M.query(subject__prefix='amaz').count(), 1)
        Article.objects.filter(pk=3).update(subject='hey #tgif')

        # reindex all
        M.run_index_all()
        # refresh index
        M.refresh_index()

        # should
        self.assertEqual(M.query(subject__prefix='amaz').count(), 0)
        self.assertEqual(M.query(subject__match='#tgif').count(), 1)

        # update some contents
        self.assertEqual(M.query(content__term='yo').count(), 1)
        Article.objects.filter(pk=3).update(content='monday uh!')

        # refresh index
        M.refresh_index()

        self.assertEqual(M.query(content__term='yo').count(), 0)
        self.assertEqual(M.query(content__term='monday').count(), 1)

    def test_query_string(self):
        # Match

        self.assertEqual(M.query(subject__match='WorkS').count(), 1)
        self.assertEqual(M.query(subject__match='works').count(), 1)
        self.assertEqual(M.query(subject__match='amaz').count(), 0)
        self.assertEqual(M.query(**{'author.username__match': 'Louise'}).count(), 2)  # noqa

        # Match phrase
        self.assertEqual(M.query(subject__match_phrase='make it ').count(), 1)
        self.assertEqual(M.query(subject__match_phrase='make i ').count(), 0)

        # Prefix
        self.assertEqual(M.query(subject__prefix='amaz').count(), 1)
        self.assertEqual(M.query(**{'author.username__prefix': 'lo'}).count(), 2)  # noqa
        self.assertEqual(M.query(**{'category.name__prefix': 'tes'}).count(), 2)  # noqa

        # Term
        self.assertEqual(M.query(**{'category.name__term': 'tes'}).count(), 0)
        self.assertEqual(M.query(**{'category.name__term': 'tests'}).count(), 2)  # noqa

        # Terms
        self.assertEqual(M.query(**{'category.name__terms': ['tests', 'category']}).count(), 3)  # noqa

        # in
        self.assertEqual(M.query(**{'category.name__in': ['tests', 'category']}).count(), 3)  # noqa

    @freeze_time('2014-10-16 16:19:20')
    def test_query_range(self):

        self.assertEqual(M.query(status__gt=0).count(), 3)
        self.assertEqual(M.query(status__gte=0).count(), 4)
        self.assertEqual(M.query(status__lt=2).count(), 2)
        self.assertEqual(M.query(status__lte=2).count(), 3)

        self.assertEqual(M.query(**{'status__gt': 1, 'status__lte': 3}).count(), 2)  # noqa
        self.assertEqual(M.query(**{'status__range': [1, 2]}).count(), 2)  # noqa

        # in
        self.assertEqual(M.query(**{'status__in': [1, 2]}).count(), 2)  # noqa

        # date range
        query_date = self.freezed_time(2014, 10, 16, 16, 19, 20)
        self.assertEqual(M.query(**{'created_at__lt': query_date}).count(), 1)

    @freeze_time('2014-10-17 16:19:20')
    def test_query_fuzzy(self):
        # http://elasticutils.readthedocs.org/en/latest/api.html?highlight=fuzzy  # noqa

        #self.assertEqual(M.query(status__fuzzy=(1, 1)).count(), 3)
        query_date = self.freezed_time(2014, 10, 17, 16, 19, 20)
        self.assertEqual(M.query(created_at__fuzzy=(query_date, '1d')).count(), 2)  # noqa

        self.assertEqual(M.query(subject__fuzzy='works').count(), 1)  # noqa
        self.assertEqual(M.query(**{'category.name__fuzzy': 'tests'}).count(), 2)  # noqa

    def test_query_wild_card(self):
        self.assertEqual(M.query(subject__wildcard='ma?e').count(), 1)
        self.assertEqual(M.query(subject__wildcard='a?ing').count(), 0)

        self.assertEqual(M.query(subject__wildcard='a*ing').count(), 1)

    """
    def test_query_distance(self):
        # TODO
    """


class FilterTestCase(BaseTest):
    fixtures = ['test_data']

    def test_filter_term_string(self):
        search_terms = {'subject': 'amazing'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=None,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)
        # Test formed filter
        subject_filter = filter_set.get_filter('subject', 'amazing').__repr__()
        self.assertEqual(F(**{'subject': 'amazing'}).__repr__(), subject_filter)  # noqa

        filtered_qs = filter_set.qs

        self.assertEqual(filtered_qs.count(), 1)

    def test_filter_prefix_or_startswith(self):
        default_action = 'prefix'
        search_terms = {'category.name': 'tes'}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=None,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=default_action)

        self.assertEqual(filter_set.qs.count(), 2)

        search_actions = {'category.name': 'prefix'}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        subject_filter = filter_set.get_filter('category.name', 'tes').__repr__()  # noqa
        self.assertEqual(F(**{'category.name__prefix': 'tes'}).__repr__(), subject_filter)  # noqa

        default_action = 'startswith'
        search_terms = {'category.name': 'tes'}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=None,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=default_action)

        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.count, 2)

        search_actions = {'category.name': 'startswith'}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action='prefix')

        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.count, 2)

        subject_filter = filter_set.get_filter('category.name', 'tes').__repr__()  # noqa
        self.assertEqual(F(**{'category.name__startswith': 'tes'}).__repr__(), subject_filter)  # noqa

    def test_filter_nested(self):
        search_terms = {'contributors': ['louise']}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=None,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        query = filter_set.qs
        self.assertEqual(query.count(), 2)
        filters = query.build_search()

        self.assertEqual(filters['filter'], filter_set._get_filter_nested_item('contributors', 'louise'))  # noqa

        search_terms = {'contributors': ['louise', 'florent']}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=None,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        query = filter_set.qs
        self.assertEqual(query.count(), 1)

    def test_filter_ids(self):
        search_terms = {'ids': [1, 2]}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=None,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        query = filter_set.qs
        self.assertEqual(query.count(), 2)

        ids_filter = query.build_search()['filter']
        self.assertEqual(ids_filter, filter_set.get_filter_ids([1, 2]))

    def test_filter_multiple_fields(self):
        search_terms = {'ids': [1, 2],
                        'contributors': ['louise', 'florent'],
                        'category.name': 'tes'}
        search_actions = {'category.name': 'startswith'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)
        query = filter_set.qs
        self.assertEqual(query.count(), 0)

        ids_filter = query.build_search()['filter']

        search_terms = {'subject': 'amazing',
                        'category.name': 'tes'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        query = filter_set.qs
        self.assertEqual(query.count(), 1)

    def test_filter_range_and_in(self):

        search_terms = {'status': 0}
        search_actions = {'status': 'gt'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        self.assertEqual(filter_set.qs.count(), 3)

        search_terms = {'status': 0}
        search_actions = {'status': 'gte'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        self.assertEqual(filter_set.qs.count(), 4)

        search_terms = {'status': 1}
        search_actions = {'status': 'lt'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        self.assertEqual(filter_set.qs.count(), 1)

        search_terms = {'status': 1}
        search_actions = {'status': 'lte'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        self.assertEqual(filter_set.qs.count(), 2)

        search_terms = {'status': [1, 2]}
        search_actions = {'status': 'range'}

        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        self.assertEqual(filter_set.qs.count(), 2)

        # in

        search_terms = {'status': [1, 2]}
        search_actions = {'status': 'in'}
        filter_set = ElasticutilsFilterSet(search_fields=self.search_fields,
                                           search_actions=search_actions,
                                           search_terms=search_terms,
                                           mapping_type=self.mapping_type,
                                           queryset=M.query(),
                                           default_action=None)

        self.assertEqual(filter_set.qs.count(), 2)

    """
    def test_filter_distance(self):
        # TODO

    """
