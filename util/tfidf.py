# -*- coding: utf-8 -*-
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


class TfIdf:
    """
    TfIdf: (term frequency–inverse document frequency) numerical statistic that is intended to
            reflect how important a word is to a document in a collection or corpus. The tf-idf
            value increases proportionally to the number of times a word appears in the document,
            but is offset by the frequency of the word in the corpus, which helps to
            adjust for the fact that some words appear more frequently in general.
    """

    def __init__(self, _corpus, _keyWordNum):
        """
        :arg: _corpus: (array) array of articles
        :arg: _keyWordNum: (int) top 30 keywords of the article
        """
        self.corpus = _corpus
        self.keyWordNum = _keyWordNum
        self.features = []
        self.tfidf_weight = []
        self.tfidf_matrix = []
        self.keywordsArr = []
        self.wordsArr = []

    def tfidf(self):
        """
            public call method
        """
        self.__tfidf()
        self.__tfidf_keywords()
        return self

    def __tfidf(self, _ngram_range=(1,1) ):
        """
        :arg: _ngram_range: tuple (min_n, max_n) The lower and upper boundary of the range of n-values for different n-grams to be extracted.
        """
        tf = TfidfVectorizer(analyzer='word', ngram_range=_ngram_range, min_df = 0, stop_words='english')
        self.tfidf_matrix = tf.fit_transform(self.corpus)
        self.features = tf.get_feature_names()
        self.tfidf_weight = self.tfidf_matrix.todense()
        self.articleNum = (len(self.tfidf_weight))
        return self

    def __tfidf_keywords(self):
        """
        1. Calculate keywordsArr: keywords and score in json format
        2. Calculate wordsArr: pure keywords
        """
        for n in range(self.articleNum):
            scoreArr = []
            words = []
            episode = self.tfidf_weight[n].tolist()[0]
            phrase_scores = [pair for pair in zip(range(0, len(episode)), episode) if pair[1] > 0]
            sorted_phrase_scores = sorted(phrase_scores, key=lambda x: x[1], reverse = True)
            for word_id, score in sorted_phrase_scores[:self.keyWordNum]:
                for phrase, score in [(self.features[word_id], score)]:
                    #print('{0: <20} {1}'.format(phrase, score))
                    #@@ TODO: add filter words list
                    scoreArr.append({phrase: score})
                    words.append(phrase)

            json_data = json.dumps(scoreArr)
            self.keywordsArr.append(json_data)
            self.wordsArr.append(words)


    def tfidf_basic(self):
        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        X = vectorizer.fit_transform(self.corpus)
        print("\nTransform Matric: ")
        print(X.toarray())
        print("\nTransform Matric shape: ")
        print (X.shape)

        words = vectorizer.get_features() #所有文章的關鍵字
        print ("\nAll feature(keywords)所有文章的字: ")
        print (words)

        # Matrix with one row per document and one column per token (e.g. word) occurring in the corpus.
        # tfidf_matrix: [n_samples, n_features_new]
        tfidf_matrix = transformer.fit_transform(X)

        tfidf_weight = tfidf_matrix.toarray()  #對應的tfidf矩陣
        print ("\ntf-idf Matric: ")
        print (tfidf_weight)
        print (tfidf_weight.shape) # 4 * 9
        return [words, tfidf_weight]

