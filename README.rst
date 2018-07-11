Similar Posts Plugin for Pelican
================================

This `Pelican <https://getpelican.com>`_ plugin adds the ``similar_posts``
variable to every published article's context.

The inputs to the similarity measurement algorithm are article tags. Thus, for
this plugin to be of any use, at least some of your articles must have a
``tags`` element in their `metadata
<http://docs.getpelican.com/en/stable/content.html#file-metadata>`_.

The ``similar_posts`` variable is a list of ``Article`` objects, or an empty
list if no articles could be found with at least one tag in common with the
given article. The list is sorted by descending similarity, then by descending
date.


Similarity score
----------------

The measure of similarity is based on the `vector space model
<https://en.wikipedia.org/wiki/Vector_space_model>`_, which represents text
documents as vectors. Each vector component corresponds to one of the terms
that exists in the corpus. Thus the corpus may be represented as a matrix whose
lines correspond to documents, and whose columns correspond to terms.

In this implementation, terms (tags) are weighted using the `tf*idf model
<https://en.wikipedia.org/wiki/Tf%E2%80%93idf>`_, which essentially means that
terms that are rare across the whole corpus have greater values than those that
are very common. The idea is that a term that is present in a great number of
documents does not provide much specificity; it does not help relate a document
to another in particular as much as a term that occurs in only a few documents.

Say we have a corpus with 5 terms. A document's vector might look like::

    [.9, .1, .0, .0, .3]

This document has 3 terms. The first one has a high value, meaning it is
relatively rare across the whole corpus. The second one has a low value,
meaning it is much more common. The next two terms are absent from this
document, while the last term is present and also somewhat common in the
corpus, although not as common as the second term. If, for example, another
document contains only the first and last terms, it should be considered more
relevant to this document than another that would have just the first and
second terms, or just the second and last terms.

We measure the similarity of two documents by computing the cosine of the angle
between their unit vectors. The resulting "score" is bounded in [0, 1]. Two
vectors with the same orientation have a `cosine similarity
<https://en.wikipedia.org/wiki/Cosine_similarity>`_ of 1. The lower the value,
the greater the angle between the vectors; the more "dissimilar" the documents
are.


Comparison with the Related Posts plugin
----------------------------------------

The `Related Posts plugin
<https://github.com/getpelican/pelican-plugins/tree/master/related_posts>`_
relates articles that have the greater number of tags in common, without any
tag weighting. If many articles match with the same number of tags, they all
get the same score. On most websites, the list of recommended articles is
short, so the most relevant ones will often be left out if all have the same
score.

Perhaps to circumvent this problem, the plugin allows one to manually link
related posts by slug. However, that creates a content maintenance burden; old
posts will not link to newer ones, unless they are manually edited to add them.


Requirements
------------

This plugin has been tested on Python 3.6.

It depends on `Gensim <https://radimrehurek.com/gensim/index.html>`_, which has
its own dependencies such as `NumPy <http://www.numpy.org/>`_, `SciPy
<https://www.scipy.org/>`_, and `smart_open <https://pypi.org/project/smart_open/>`_.


Installation
------------

To install this plugin, see `How to use plugins
<http://docs.getpelican.com/en/latest/plugins.html>`__ from the Pelican
documentation.

Before using it, also install the required libraries::

    pip install -r requirements.txt

By default, up to 5 articles are listed. You may customize this value by
defining ``SIMILAR_POSTS_MAX_COUNT`` in your settings file, e.g.::

    SIMILAR_POSTS_MAX_COUNT = 10

You may also define ``SIMILAR_POSTS_MIN_SCORE`` in the settings file. It
defaults to .0001. A value of 1.0 would restrict the list of similar posts to
articles that share the same list of tags. Any value in between could act as a
similarity threshold, but you'll probably have to find the proper value
empirically.

You can output the ``similar_posts`` variable in your article template. This
might look like the following:

.. code-block:: html+jinja

    {% if article.similar_posts %}
        <ul>
        {% for similar in article.similar_posts %}
            <li><a href="{{ SITEURL }}/{{ similar.url }}">{{ similar.title }}</a></li>
        {% endfor %}
        </ul>
    {% endif %}
