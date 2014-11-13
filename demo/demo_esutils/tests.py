from django.contrib.auth.models import User
from django.test import TestCase

from demo_esutils.models import Category
from demo_esutils.models import Article
from demo_esutils.mappings import ArticleMappingType as M


class MappingTestCase(TestCase):

    def setUp(self):

        M.update_mapping()

        self.florent = User.objects.create(username='florent',
                                           email='florent@demo.es')

        self.louise = User.objects.create(username='louise',
                                          email='louise@demo.es')

    def tearDown(self):
        self.florent.delete()
        self.louise.delete()

        Category.objects.all().delete()
        Article.objects.all().delete()
        M.refresh_index()

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

        self.assertEqual(M.query(subject__match='My Am').count(), 1)
        self.assertEqual(M.query(subject__match='WorkS').count(), 1)
        self.assertEqual(M.query(subject__match='works').count(), 1)
        self.assertEqual(M.query(subject__prefix='amaz').count(), 1)
        self.assertEqual(M.query(subject__match='amaz').count(), 0)

        self.assertEqual(M.query(**{'author-username__prefix':'lo'}).count(), 1)
        self.assertEqual(M.query(**{'author-username__match':'Louise'}).count(), 1)

        self.assertEqual(M.query(**{'category-name__prefix': 'tes'}).count(), 2)
        self.assertEqual(M.query(**{'category-name__term': 'tes'}).count(), 0)
        self.assertEqual(M.query(**{'category-name__term': 'tests'}).count(), 2)

        # update some contents
        Article.objects.filter(author=self.louise).update(subject='hey #tgif')

        # reindex all
        M.run_index_all()
        # refresh index
        M.refresh_index()

        # should
        self.assertEqual(M.query(subject__prefix='amaz').count(), 0)
        self.assertEqual(M.query(subject__match='#tgif').count(), 1)

        # update some contents
        Article.objects.filter(author=self.louise).update(content='monday uh!')

        # refresh index
        M.refresh_index()

        self.assertEqual(M.query(content__term='yo').count(), 0)
        self.assertEqual(M.query(content__term='monday').count(), 1)

        for i, a in enumerate([article1, article2]):
            # remove an article
            a.delete()
            # refresh index
            M.refresh_index()
            # check removed
            del_count = M.count()
            self.assertEqual(del_count, add_count - i - 1)
