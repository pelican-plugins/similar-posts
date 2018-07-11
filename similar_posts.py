"""
Similar Posts plugin for Pelican.

Adds a `similar_posts` list to every article's context.
"""

import logging
import math
import os

from pelican import signals
from itertools import chain

from gensim import corpora, models, similarities

logger = logging.getLogger(__name__)

def add_similar_posts(generator):
    max_count = generator.settings.get('SIMILAR_POSTS_MAX_COUNT', 5)
    min_score = generator.settings.get('SIMILAR_POSTS_MIN_SCORE', .0001)

    # Collect all documents. A document gets represented by a list of tags.
    docs = [
        [tag.name for tag in article.tags] if hasattr(article, 'tags') else []
        for article in generator.articles
    ]

    if len(docs) == 0:
        return  # No documents, nothing to do.

    # Build a dictionary of every unique tag.
    dictionary = corpora.Dictionary(docs)
    num_features = len(dictionary)

    if num_features == 0:
        return  # No tags, nothing to do.

    # Vectorize each document as a bag-of-words. This creates a sparse matrix
    # where each line corresponds to a document, and each column a feature.
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    del docs

    # Transform the vectors to tf*idf values. Here we use a tf*idf formula
    # inspired by Lucene's TFIDFSimilarity class, instead of Gensim's default
    # formula, to better handle edge cases (e.g. when all documents have the
    # same terms, df == D, which means log(D/df) == log(1) == 0, which would
    # imply no similarity!).
    tfidf = models.TfidfModel(
        corpus, normalize=True,
        wlocal=lambda tf: tf ** .5,
        wglobal=lambda df, D: .5 + math.log((D + 1) / (df + 1)))

    # Compute the cosine similarity of every document pair.
    index = similarities.MatrixSimilarity(tfidf[corpus], num_features=num_features)

    for i, (article, scores) in enumerate(zip(generator.articles, index)):
        # Obviously, article is similar to itself. Take it away.
        scores[i] = -1

        # Build (article index, score) tuples, sorted by score, then by date.
        similar = sorted(
            [item for item in enumerate(scores) if item[1] >= min_score],
            key=lambda item: (item[1], generator.articles[item[0]].date),
            reverse=True)[:max_count]

        article.similar_posts = [generator.articles[item[0]] for item in similar]

        logger.debug('{article}: similar_posts scores: {scores}'.format(
            article=os.path.basename(article.source_path) if hasattr(article, 'source_path') else i,
            scores=[item[1] for item in similar]))

def register():
    signals.article_generator_finalized.connect(add_similar_posts)
