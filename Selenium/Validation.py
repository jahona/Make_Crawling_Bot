from sklearn.feature_extraction.text import CountVectorizer
import os
import numpy as np
import sys
import nltk.stem
from sklearn.feature_extraction.text import TfidfVectorizer

class Validation():
    def __init__(self):
        self.__best_dist = sys.maxsize
        self.__best_doc = None
        self.__best_i = None
        self.__vectorizer = CountVectorizer()
        self.__dic = dict()

        self.__baseSentences = []
        self.__targetSentences = []
        self.__post_vec = None
        self.__new_post_vec = None

        self.__base_normalized = None

        self.__str = ""

    ## get
    def get_best_dist(self):
        return self.__best_dist

    def get_best_doc(self):
        return self.__best_doc

    def get_best_i(self):
        return self.__best_i

    def get_vectorizer(self):
        return self.__vectorizer

    def get_dic(self):
        return self.__dic

    def get_base_sentences(self):
        return self.__baseSentences

    def get_target_sentences(self):
        return self.__targetSentences

    def get_post_vec(self):
        return self.__post_vec

    def get_new_post_vec(self):
        return self.__new_post_vec

    def get_base_normalized(self):
        return self.__base_normalized

    ## set
    def set_best_dist(self, best_dis):
        self.__best_dist = best_dis

    def set_best_i(self, best_i):
        self.__best_i = best_i

    def set_dic(self, i, dist):
        self.__dic[i] = dist

    ## 유클리드 거리를 구하기
    def dist_norm(self):
        # 벡터 사이의 거리를 구하기 위해서는 1차원 배열을 이용해야 하기 때문에 [0], 인덱스를 지정합니다.
        post_vec = self.__post_vec.toarray()[0]
        new_post_vec = self.__new_post_vec.toarray()[0]

        # norm(): 벡터 간에 유클리드 거리를 계산
        if self.__base_normalized is None:
            self.__base_normalized = post_vec / np.linalg.norm(post_vec)

        target_normalized = new_post_vec / np.linalg.norm(new_post_vec)

        delta = self.__base_normalized - target_normalized

        return np.linalg.norm(delta)

    # 기준이 되는 문자열 배열들에 한해 vectorizer
    def base_vectorizing(self):
        rows = []
        rows.append(self.__str)
        print(self.__str)
        self.__post_vec = self.__vectorizer.fit_transform(rows)

    # 타겟이 되는 문자열들에 한해 vectorizer
    def target_vectorizing(self, sentences):
        rows = []
        str = ""
        for index, row in enumerate(sentences):
            str += row
        rows.append(str)

        self.__new_post_vec = self.__vectorizer.transform(rows)

    def sum_str(self, sentences):
        for row in sentences:
            self.__str += row
