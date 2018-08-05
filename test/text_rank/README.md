# Install Package

### Newspaper

사용자가 입력한 url 에서 text 를 크롤링 해주는 패키지이다.

- python3 : `pip install newspaper3k`

### KoNLPy

한글형태소 분석기로 TextRank 적용하기 위한 전처리 과정으로 사용된다.

- `pip install jpype1`
- `pip install konlpy`

### Scikit-learn

머신러닝 패키지로 TF-IDF 모델을 생성하는데 사용된다.

- `pip install scikit-learn`

import source code example

```
from newspaper import Article
from konlpy.tag import Kkma
from konlpy.tag import Twitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np
```
