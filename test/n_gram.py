from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import re
import string
import pprint

def cleanInput(input):
    input = re.sub('\n+', " ", input)
    input = re.sub('\[[0-9]*\]', "", input)
    input = re.sub(' +', " ", input)
    input = bytes(input, "UTF-8")
    input = input.decode("ascii", "ignore")
    cleanInput = []
    input = input.split(' ')
    for item in input:
        item = item.strip(string.punctuation)
        if len(item) > 1 or (item.lower() == 'a' or item.lower() == 'i'):
            cleanInput.append(item)
    return cleanInput

def ngrams(input, n):
    input = cleanInput(input)
    output = []
    for i in range(len(input)-n+1):
        output.append(input[i:i+n])
    return output

gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
html = urlopen("http://en.wikipedia.org/wiki/Python_(programming_language)", context=gcontext)
bsObj = BeautifulSoup(html, "html.parser")
content = bsObj.find("div", {"id":"mw-content-text"}).get_text()
ngrams = ngrams(content, 2)
ngrams = sorted(ngrams, key=lambda t: t[1], reverse=True)

pp = pprint.PrettyPrinter(indent=4)
w_count = {};
for ngram in ngrams:
    try:
        w_count[ngram[1]] += 1
    except:
        w_count[ngram[1]]=1

pp.pprint(w_count)
print("2-grams count is: " + str(len(ngrams)))
