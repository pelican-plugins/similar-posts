import datetime
import unittest
from pelican.urlwrappers import Tag

from similar_posts import add_similar_posts


class PseudoArticlesGenerator():
    """A fake Generator, with just the attributes that are actually needed by the plugin."""
    def __init__(self, settings=None, articles=None):
        self.settings = settings or {}
        self.articles = articles or []


class PseudoArticle():
    """A fake Article, with just the attributes that are actually needed by the plugin."""
    def __init__(self, tag_names=None, date=()):
        if tag_names:
            self.tags = [Tag(name=name, settings={}) for name in tag_names]

        if date:
            self.date = datetime.datetime(*date)
        else:
            self.date = datetime.datetime(1970, 1, 1)

    def __repr__(self):
        return f'{self.__class__.__name__}({[t.name for t in self.tags]!r})'


class NoArticlesTestCase(unittest.TestCase):
    """Test that a generator with no articles raises no exception."""

    def setUp(self):
        self.generator = PseudoArticlesGenerator()
        add_similar_posts(self.generator)

    def test_no_articles(self):
        pass


class SingleArticleTestCase(unittest.TestCase):
    """Test a generator that only has a single article."""

    def setUp(self):
        self.generator = PseudoArticlesGenerator(
            articles=[PseudoArticle(['tag1', 'tag2'])])
        add_similar_posts(self.generator)

    def test_no_similar(self):
        self.assertFalse(self.generator.articles[0].similar_posts)


class NoTagsTestCase(unittest.TestCase):
    """Test that a generator whose articles have no tags raises no exception."""

    def setUp(self):
        self.generator = PseudoArticlesGenerator(
            articles=[PseudoArticle(), PseudoArticle(), PseudoArticle()])
        add_similar_posts(self.generator)

    def test_no_tags(self):
        pass


class IdenticalTagsTestCase(unittest.TestCase):
    """
    Test a generator whose articles all have the same tags.

    Some TF*IDF formulas would cause this test to fail.
    """

    def setUp(self):
        self.test_content = [
            PseudoArticle(['common']),  # 0
            PseudoArticle(['common']),  # 1
            PseudoArticle(['common']),  # 2
        ]
        self.generator = PseudoArticlesGenerator(articles=self.test_content)
        add_similar_posts(self.generator)

    def test_identical(self):
        self.assertTrue(set(self.generator.articles[0].similar_posts) ==
            {
                self.test_content[1],
                self.test_content[2],
            })
        self.assertTrue(set(self.generator.articles[1].similar_posts) ==
            {
                self.test_content[0],
                self.test_content[2],
            })
        self.assertTrue(set(self.generator.articles[2].similar_posts) ==
            {
                self.test_content[0],
                self.test_content[1],
            })


class CommonTagTestCase(unittest.TestCase):
    """
    Test a generator whose articles all have one of the tags in common.

    Some TF*IDF formulas would cause this test to fail.
    """

    def setUp(self):
        self.test_content = [
            PseudoArticle(['common', 'unique1']),  # 0
            PseudoArticle(['common', 'unique2']),  # 1
            PseudoArticle(['common', 'unique3']),  # 2
        ]
        self.generator = PseudoArticlesGenerator(articles=self.test_content)
        add_similar_posts(self.generator)

    def test_common(self):
        self.assertTrue(set(self.generator.articles[0].similar_posts) ==
            {
                self.test_content[1],
                self.test_content[2],
            })
        self.assertTrue(set(self.generator.articles[1].similar_posts) ==
            {
                self.test_content[0],
                self.test_content[2],
            })
        self.assertTrue(set(self.generator.articles[2].similar_posts) ==
            {
                self.test_content[0],
                self.test_content[1],
            })


class UniqueTestCase(unittest.TestCase):
    """Test a generator whose every article has unique tags."""

    def setUp(self):
        self.generator = PseudoArticlesGenerator(
            articles=[
                PseudoArticle(),
                PseudoArticle(['unique1']),
                PseudoArticle(['unique2', 'unique3']),
                PseudoArticle(['unique4', 'unique5', 'unique6']),
            ])
        add_similar_posts(self.generator)

    def test_unique(self):
        for article in self.generator.articles:
            self.assertFalse(article.similar_posts)


class SimilarityTestCase(unittest.TestCase):
    """Test that articles that have tags in common are considered similar."""

    def setUp(self):
        self.test_content = [
            PseudoArticle(['common1']),                        # 0
            PseudoArticle(['common2']),                        # 1
            PseudoArticle(['common2', 'common1']),             # 2
            PseudoArticle(['common2', 'unique1']),             # 3
            PseudoArticle(['unique2', 'unique3']),             # 4
            PseudoArticle(['common2', 'unique4', 'unique5']),  # 5
            PseudoArticle(['common2']),                        # 6
        ]
        self.generator = PseudoArticlesGenerator(articles=self.test_content)
        add_similar_posts(self.generator)

    def test_similar_posts(self):
        self.assertTrue(set(self.generator.articles[0].similar_posts) ==
            {self.test_content[2]})
        self.assertTrue(set(self.generator.articles[1].similar_posts) ==
            {
                self.test_content[2],
                self.test_content[3],
                self.test_content[5],
                self.test_content[6],
            })
        self.assertTrue(set(self.generator.articles[2].similar_posts) ==
            {
                self.test_content[0],
                self.test_content[1],
                self.test_content[3],
                self.test_content[5],
                self.test_content[6],
            })
        self.assertTrue(set(self.generator.articles[3].similar_posts) ==
            {
                self.test_content[1],
                self.test_content[2],
                self.test_content[5],
                self.test_content[6],
            })
        self.assertFalse(self.generator.articles[4].similar_posts)
        self.assertTrue(set(self.generator.articles[5].similar_posts) ==
            {
                self.test_content[1],
                self.test_content[2],
                self.test_content[3],
                self.test_content[6],
            })
        self.assertTrue(set(self.generator.articles[6].similar_posts) ==
            {
                self.test_content[1],
                self.test_content[2],
                self.test_content[3],
                self.test_content[5],
            })


class MaxCountSettingTestCase(unittest.TestCase):
    """Test the SIMILAR_POSTS_MAX_COUNT setting."""

    def setUp(self):
        self.test_content = [
            PseudoArticle(['common']),
            PseudoArticle(['common']),
            PseudoArticle(['common']),
            PseudoArticle(['common']),
        ]
        self.generator = PseudoArticlesGenerator(
            articles=self.test_content, settings={'SIMILAR_POSTS_MAX_COUNT': 2})
        add_similar_posts(self.generator)

    def test_max_count(self):
        for article in self.generator.articles:
            self.assertTrue(len(article.similar_posts) == 2)


class MinScoreSettingTestCase(unittest.TestCase):
    """Test the SIMILAR_POSTS_MIN_SCORE setting."""

    def setUp(self):
        self.test_content = [
            PseudoArticle(['common1']),            # 0
            PseudoArticle(['common1', 'unique']),  # 1
            PseudoArticle(['common2']),            # 2
            PseudoArticle(['common2']),            # 3
        ]
        self.generator = PseudoArticlesGenerator(
            articles=self.test_content, settings={'SIMILAR_POSTS_MIN_SCORE': 1.0})
        add_similar_posts(self.generator)

    def test_not_similar_enough(self):
        self.assertFalse(self.generator.articles[0].similar_posts)
        self.assertFalse(self.generator.articles[1].similar_posts)

    def test_identical(self):
        self.assertTrue(set(self.generator.articles[2].similar_posts) ==
            {self.test_content[3]})
        self.assertTrue(set(self.generator.articles[3].similar_posts) ==
            {self.test_content[2]})


class OrderingTestCase(unittest.TestCase):
    """Test the ordering of similar posts."""

    def setUp(self):
        self.test_content = [
            PseudoArticle(['common1', 'unique1', 'unique2']),  # 0
            PseudoArticle(['common1', 'common2', 'unique3']),  # 1
            PseudoArticle(['common1', 'common2', 'unique4']),  # 2
            PseudoArticle(['common3'], (2016,1,1)),            # 3
            PseudoArticle(['common3'], (2018,1,1)),            # 4
            PseudoArticle(['common3'], (2017,1,1)),            # 5
        ]
        self.generator = PseudoArticlesGenerator(articles=self.test_content)
        add_similar_posts(self.generator)

    def test_score_ordering(self):
        self.assertTrue(self.generator.articles[1].similar_posts ==
            [
                self.test_content[2],
                self.test_content[0],
            ])
        self.assertTrue(self.generator.articles[2].similar_posts ==
            [
                self.test_content[1],
                self.test_content[0],
            ])

    def test_date_ordering(self):
        self.assertTrue(self.generator.articles[3].similar_posts ==
            [
                self.test_content[4],
                self.test_content[5],
            ])
        self.assertTrue(self.generator.articles[4].similar_posts ==
            [
                self.test_content[5],
                self.test_content[3],
            ])
        self.assertTrue(self.generator.articles[5].similar_posts ==
            [
                self.test_content[4],
                self.test_content[3],
            ])


if __name__ == '__main__':
    unittest.main()
