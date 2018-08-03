from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import re

def ngrams(input, n):
    input = re.sub('\n+', " ", input)
    input = re.sub(' +', " ", input)
    input = bytes(input, "UTF-8")
    input = input.decode("ascii", "ignore")
    print(input)

    input = input.split(' ')
    output = []
    for i in range(len(input)-n+1):
        output.append(input[i:i+n])
    return output

gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
html = urlopen("http://en.wikipedia.org/wiki/Python_(programming_language)", context=gcontext)
bsObj = BeautifulSoup(html, "html.parser")
content = bsObj.find("div", {"id":"mw-content-text"}).get_text()
ngramsData = ngrams(content, 2)
print(ngramsData)
print("2-grams count is: " + str(len(ngramsData)))
