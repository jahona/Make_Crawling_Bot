# from newspaper import Article
from konlpy.tag import Kkma
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np
import CustomizingArticle

'''
Step1. 문서 타입에 따른 문장 단위로 분리
'''
class SentenceTokenizer(object):
    def __init__(self):
        self.kkma = Kkma()
        self.Okt = Okt()
        self.stopwords = ['처음', '널리', '반드시', '완전', '매일', '보통', '이내', '바깥', '지금', '또한', '현재', '오늘날', '정말', '조금',
        '거꾸로', '위주', '심지어', '저절로', '와중', '사이', '다른', '하나', '주로', '대부분', '아래', '거나', '첫째', '대한', '우선', '주신',
        '부분', '한편', '여러', '거의', '자체', '바로', '대해', '만약', '마치', '이하', '모두', '따라서', '아마', '둘째', '그게', '직접', '평소',
        '보기', '지난', '별로', '번은', '실제', '이후', '때문', '면서', '당시', '반면', '한참', '통해', '마찬가지', '오늘', '항시', '다소', '모든',
        '매우', '말로', '요즘', '혹시', '다시', '대충', '미리', '그냥', '즉시', '동안', '크게', '부터', '통한', '점점', '한번', '정도', '제대로',
        '최근', '이번', '서로', '먼저', '헤이', '우리', '이건', '위해', '이상', '로써', '이전', '일부', '사실', '내일', '이제', '오히려',
        '중인', '만큼', '아', '휴', '아이구', '아이쿠', '아이고', '어', '나', '저희', '따라', '의해', '을', '를', '에', '의', '가']

    # url 주소를 받아 기사내용 추출.
    def url2sentences(self, page_source):
        article = CustomizingArticle.Article(language='ko') # newpaper
        article.set_html(page_source)
        article.parse()

        # kkma를 이용해 문장단위로 분리하여 배열 리턴
        sentences = self.kkma.sentences(article.text)

        return sentences

    # text 를 입력받아 문장단위로 분리하여 배열 리턴
    def text2sentences(self, page_source):
        article = CustomizingArticle.Article(language='ko') # newpaper
        article.set_html(page_source)
        article.parse()

        sentences = self.kkma.sentences(article.text)

        return sentences

    # sentences 로부터 Okt.nouns()를 이용하여 명사 추출 후 배열 리턴
    def get_nouns(self, sentences):
        nouns = []
        for sentence in sentences:
            if sentence is not '':
                nouns.append(' '.join([noun for noun in self.Okt.nouns(str(sentence))
                if noun not in self.stopwords and len(noun) > 1]))

        return nouns

'''
Step2. TF-IDF 모델 생성 및 그래프 생성

TF(Term Frequency) : 단어 빈도, 특정 단어가 문서 내에 얼만큼의 빈도로 등장하는지 나타내는 척도

IDF(Inverse Document Frequency) : 역문헌 빈도수, 문서 빈도의 역수로써 전체 문서 개수를 해당 단어가 포함된 문서의 개수로 나눈 것을 의미
'''
class GraphMatrix(object):
    def __init__(self):
        # TfidVectorizer() 는 collectino of raw documents들을 TF-IDF 특징을 가진 행렬로 변환한다.
        self.tfidf = TfidfVectorizer()
        # CountVectorizer() 는 collection of text documents들을 토큰 카운트 행렬로 변환시킨다.
        self.cnt_vec = CountVectorizer()
        self.graph_sentence = []

    # 명사로 이루어진 sentence를 입력받아 tfidf matrix를 만든 후 Sentence graph를 리턴
    def build_sent_graph(self, sentence):
        try:
            # fit_transform 를 이용해 sentence(=raw data)를 tfidf matrix로 변환
            tfidf_mat = self.tfidf.fit_transform(sentence).toarray()
            # numpy의 dot 함수로 두 행렬의 곱을 통해 graph_sentence를 반환
            # tfidf_mat.T는 Transpose, 즉 전치행렬을 의미한다.
            self.graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
            return self.graph_sentence
        except:
            pass

    # 명사로 이루어진 sentence를 입력받아 matrix 생성 후 word graph와 {idx:word} 형태의 딕셔너리를 리턴
    def build_words_graph(self, sentence):
        cnt_vec_mat = normalize(self.cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
        vocab = self.cnt_vec.vocabulary_

        return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word] : word for word in vocab}

'''
Step3. Text Lank Algorithm 적용
'''
class Rank(object):
    # 식을 구현한 부분으로 {idx: rank} 형태의 dictionary 를 return 한다.
    def get_ranks(self, graph, d=0.85): # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0 # diagonal 부분을 0으로
            link_sum = np.sum(A[:,id]) # A[:, id] = A[:][id]
            if link_sum != 0:
                A[:, id] /= link_sum
            A[:, id] *= -d
            A[id, id] = 1

        B = (1-d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(A, B) # 연립방정식 Ax = b

        return {idx: r[0] for idx, r in enumerate(ranks)}

'''
Step4. Text Lank Class 구현
'''
class TextRank(object):
    def __init__(self, text):
        try:
            self.sent_tokenize = SentenceTokenizer()

            if text[:5] in ('http:', 'https'):
                self.sentences = self.sent_tokenize.url2sentences(text)
            else:
                self.sentences = self.sent_tokenize.text2sentences(text)

            self.nouns = self.sent_tokenize.get_nouns(self.sentences)

            self.graph_matrix = GraphMatrix()
            self.sent_graph = self.graph_matrix.build_sent_graph(self.nouns)
            self.words_graph, self.idx2word = self.graph_matrix.build_words_graph(self.nouns)

            self.rank = Rank()
            self.sent_rank_idx = self.rank.get_ranks(self.sent_graph)
            self.sorted_sent_rank_idx = sorted(self.sent_rank_idx, key=lambda k: self.sent_rank_idx[k], reverse=True)

            self.word_rank_idx = self.rank.get_ranks(self.words_graph)
            self.sorted_word_rank_idx = sorted(self.word_rank_idx, key=lambda k: self.word_rank_idx[k], reverse=True)
        except:
            return None

    def summarize(self, sent_num=3):
        try:
            summary = []
            index=[]
            for idx in self.sorted_sent_rank_idx[:sent_num]:
                index.append(idx)

            index.sort()

            for idx in index:
                summary.append(self.sentences[idx])

            return summary
        except:
            pass

    def keywords(self, word_num=10):
        try:
            rank = Rank()
            rank_idx = rank.get_ranks(self.words_graph)
            sorted_rank_idx = sorted(rank_idx, key=lambda k: rank_idx[k], reverse=True)

            keywords = []
            index=[]

            for idx in sorted_rank_idx[:word_num]:
                index.append(idx)

            #index.sort()
            for idx in index:
                keywords.append(self.idx2word[idx])

            return keywords
        except:
            pass
