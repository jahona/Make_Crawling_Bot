from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import re
import string
import operator
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
    output = {}
    for i in range(len(input)-n+1):
        ngramTemp = " ".join(input[i:i+n])
        if ngramTemp not in output:
            output[ngramTemp] = 0
        output[ngramTemp] += 1
    return output

gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
content = str(urlopen("http://pythonscraping.com/files/inaugurationSpeech.txt", context=gcontext).read(), 'utf-8')
ngrams = ngrams(content, 2)
# key=operator.itemgetter[index] 는 key=ngrams[index]와 같은 코드이다.
ngrams = sorted(ngrams.items(), key=operator.itemgetter(1), reverse=True)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(ngrams)
print("2-grams count is: " + str(len(ngrams)))
