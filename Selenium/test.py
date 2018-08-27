from sklearn.feature_extraction.text import CountVectorizer
import os
import numpy as np
# 거리(best_dist)는 작을수록 좋습니다. 그렇기 때문에 초기값으로 일단 큰 값을 입력해 놓습니다.
import sys
best_dist = sys.maxsize
best_doc = None
best_i = None

import nltk.stem
from sklearn.feature_extraction.text import TfidfVectorizer

english_stemmer = nltk.stem.SnowballStemmer('english')

class StemmedCountVector(TfidfVectorizer):
    # CountVectorizer의 build_analyzer 함수를 재정의 합니다.
    def build_analyzer(self):
        analyzer = super(StemmedCountVector, self).build_analyzer()
        # 토큰화 된 단어(w)를 어근화(stem) 시킨 후 리턴합니다.
        return lambda doc: (english_stemmer.stem(w) for w in analyzer(doc))

def dist_norm(v1, v2):
    v1_normalized = v1/np.linalg.norm(v1)
    v2_normalized = v2/np.linalg.norm(v2)
    delta = v1_normalized - v2_normalized
    # norm(): 벡터 간에 유클리드 거리를 계산
    return np.linalg.norm(delta)

posts = ["This is a toy post about machine learning. Actually, it contains not much interesting stuff.",
"Imaging databases provide storage capabilities.",
"Most imaging databases save images permanently.",
"Imaging databases store data.",
"Imaging databases store data. Imaging databases store data. Imaging databases store data."]

# Count Vector를 만들었습니다. stop_words 인자는 불용어를 의미합니다.
vectorizer = StemmedCountVector(min_df=1, stop_words="english", decode_error='ignore')

X_train = vectorizer.fit_transform(posts)

new_post = "imaging databases"
new_post_vec = vectorizer.transform([new_post])

for i, post in enumerate(posts):
    post_vec = X_train.toarray()[i]
    # 벡터 사이의 거리를 구하기 위해서는 1차원 배열을 이용해야 하기 때문에 [0], 인덱스를 지정합니다.
    d = dist_norm(post_vec, new_post_vec.toarray()[0])
    print("=== Post %i with dist = %.2f: %s" %(i, d, post))
    if d<best_dist:
        best_dist = d
        best_i = i

print("Best post is %i with dist=%.2f" % (best_i, best_dist))
