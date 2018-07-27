from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime
import random
import ssl
from time import sleep

pages = set()
random.seed(datetime.datetime.now())

# 페이지에 발견된 내부 링크를 모두 목록으로 만듭니다.
def getInternalLinks(bsObj, includeUrl):
	internalLinks = []
	# /로 시작하는 링크를 모두 찾습니다.
	for link in bsObj.findAll("a", href=re.compile("^(/|.*"+includeUrl+")")):
		if link.attrs['href'] is not None:
			if link.attrs['href'] not in internalLinks:
				internalLinks.append(link.attrs['href'])
	return getInternalLinks

# 페이지에서 발견된 외부 링크를 모두 목록으로 만듭니다.
def getExternalLinks(bsObj, excludeUrl):
	externalLinks = []
	# 현재 URL을 포함하지 않으면서 http나 www로 시작하는 링크를 모두 찾습니다.
	for link in bsObj.findAll("a", href=re.compile("^(http|www)((?!"+excludeUrl+").)*$")):
		if link.attrs['href'] is not None:
			if link.attrs['href'] not in externalLinks:
				externalLinks.append(link.attrs['href'])
	return externalLinks

def splitAddress(fullAddress):
	hostParts = fullAddress.replace("http://", "").split("/")
	return hostParts

def getRandomExternalLink(startingAddress):
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

	html = urlopen(startingAddress, context=gcontext)

	bsObj = BeautifulSoup(html, "html.parser")

	externalLinks = getExternalLinks(bsObj, splitAddress(startingAddress)[0])

	for link in externalLinks:
		print(link)

	if len(externalLinks) == 0:
		internalLinks = getInternalLinks(startingPage)
		return getNextExternalLInk(internalLinks[random.randint(0, len(internalLinks)-1)])
	else:
		return externalLinks[random.randint(0, len(externalLinks)-1)]

def followExternalOnly(startingSite):
	externalLink = getRandomExternalLink("http://oreilly.com")
	print("Random external link is: "+externalLink)
	sleep(1)
	followExternalOnly(externalLink)

followExternalOnly("http://oreilly.com")
