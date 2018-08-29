from sklearn.feature_extraction.text import CountVectorizer
import os
import numpy as np
import sys
import nltk.stem
from sklearn.feature_extraction.text import TfidfVectorizer

# english_stemmer = nltk.stem.SnowballStemmer('english')

# class StemmedCountVector(TfidfVectorizer):
#     # CountVectorizer의 build_analyzer 함수를 재정의 합니다.
#     def build_analyzer(self):
#         analyzer = super(StemmedCountVector, self).build_analyzer()
#         # 토큰화 된 단어(w)를 어근화(stem) 시킨 후 리턴합니다.
#         return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))
class Document_similarity():
    def __init__(self):
        self.best_dist = sys.maxsize
        self.best_doc = None
        self.best_i = None
        self.vectorizer = CountVectorizer(min_df=1, stop_words="english")
        self.dic = dict()

        self.baseSentences = []
        self.targetSentences = []
        self.post_vec = None
        self.new_post_vec = None

        self.base_normalized = None

    def get_best_dist(self):
        return self.best_dist

    def get_best_doc(self):
        return self.best_doc

    def get_best_i(self):
        return self.best_i

    def get_target_sentences(self):
        return self.targetSentences

    def get_base_sentences(self):
        return self.basepageSource

    def get_vectorizer(self):
        return self.vectorizer

    def set_best_dist(self, best_dis):
        self.best_dist = best_dis

    def set_best_i(self, best_i):
        self.best_i = best_i

    def get_post_vec(self):
        return self.post_vec

    def get_new_post_vec(self):
        return self.new_post_vec

    def get_dic(self):
        return self.dic

    def set_dic(self, i, dist):
        self.dic[i] = dist

    def dist_norm(self, v1, v2):
        if self.base_normalized is None:
            self.base_normalized = v1 / np.linalg.norm(v1)

        target_normalized = v2 / np.linalg.norm(v2)

        delta = self.base_normalized - target_normalized
        # norm(): 벡터 간에 유클리드 거리를 계산
        return np.linalg.norm(delta)

    def add_sentences_to_base(self, sentences):
        self.baseSentences += sentences

    def set_target_sentence(self, sentences):
        self.targetSentences = sentences

    def base_vectorizing(self):
        self.post_vec = self.vectorizer.fit_transform(self.baseSentences)

    def target_vectorizing(self):
        self.new_post_vec = self.vectorizer.transform(self.targetSentences)


# D_S = Document_similarity()
# D_S.set_basepagesouce("This is a toy post about machine learning. Actually ")
# D_S.set_basepagesouce("Imaging databases provide storage capabilities.")
# D_S.set_pagesource("imaging databases")
# D_S.vectorizing()
#
# for i, pageSource in enumerate(D_S.get_basepageSource()):
#     # 벡터 사이의 거리를 구하기 위해서는 1차원 배열을 이용해야 하기 때문에 [0], 인덱스를 지정합니다.
#     d = D_S.dist_norm(D_S.get_post_vec().toarray()[i], D_S.get_new_post_vec().toarray()[0])
#     print("=== Post %i with dist = %.2f: %s" %(i, d, pageSource))
#     if d<D_S.get_best_dist():
#         D_S.set_best_dist(d)
#         D_S.set_best_i(i)
#
# print("Best post is %i with dist=%.2f" % (D_S.get_best_i(), D_S.get_best_dist()))
