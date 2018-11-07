from sklearn.feature_extraction.text import CountVectorizer
import os
import numpy as np
import sys
import nltk.stem
from sklearn.feature_extraction.text import TfidfVectorizer

class Validation():
    def __init__(self):
        self.__vectorizer = CountVectorizer()
        self.__dic = dict()

        self.__baseSentences = []
        self.__targetSentences = []
        self.__post_vec = None
        self.__new_post_vec = None

        self.__base_normalized = None

        self.__str = ""

    ## init
    def init_dic(self):
        self.__dic = dict()

    def init_base_normalized(self):
        self.__base_normalized = None

    ## get
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
    def set_dic(self, i, dist):
        self.__dic[i] = dist

    ## 유클리드 거리를 구하기
    def dist_norm(self):
        try:
            # 벡터 사이의 거리를 구하기 위해서는 1차원 배열을 이용해야 하기 때문에 [0], 인덱스를 지정합니다.
            post_vec = self.__post_vec.toarray()[0]
            new_post_vec = self.__new_post_vec.toarray()[0]

            # norm(): 벡터 간에 유클리드 거리를 계산
            if self.__base_normalized is None:
                self.__base_normalized = post_vec / np.linalg.norm(post_vec)

            target_normalized = new_post_vec / np.linalg.norm(new_post_vec)

            delta = self.__base_normalized - target_normalized
        except:
            print('유클리드 거리 구하기 에러')

        return np.linalg.norm(delta)

    # 기준이 되는 문자열 배열들에 한해 vectorizer
    def base_vectorizing(self):
        print(self.__str)
        self.__post_vec = self.__vectorizer.fit_transform([self.__str])
        self.__str = ""

    # 타겟이 되는 문자열들에 한해 vectorizer
    def target_vectorizing(self, sentences):
        strings = ""

        for row in sentences:
            strings += ' ' + row

        self.__new_post_vec = self.__vectorizer.transform([strings])

    def sum_str(self, sentences):
        for row in sentences:
            self.__str += ' ' + row

# validation = Validation()

# baseList = ["안녕하세요", "안녕 보혁아", "보혁"]
# targetList = ["기범 보혁"]

# validation.sum_str(baseList)
# validation.base_vectorizing()
# validation.target_vectorizing(targetList)

# print(validation.dist_norm())