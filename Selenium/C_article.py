import logging
import copy
import os
import glob

import requests

from newspaper import images
from newspaper import network
from newspaper import nlp
from newspaper import settings
from newspaper import urls

from newspaper.cleaners import DocumentCleaner
from newspaper.configuration import Configuration
from newspaper.extractors import ContentExtractor
from newspaper.outputformatters import OutputFormatter
from newspaper.utils import (URLHelper, RawHelper, extend_config,
                    get_available_languages, extract_meta_refresh)
from newspaper.videos.extractors import VideoExtractor


from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import ssl
from time import sleep
import os




log = logging.getLogger(__name__)


class ArticleDownloadState(object):
    NOT_STARTED = 0
    FAILED_RESPONSE = 1
    SUCCESS = 2


class ArticleException(Exception):
    pass


class Article(object):
    """Article objects abstract an online news article page
    """
    def __init__(self, config=None, **kwargs):
        """The **kwargs argument may be filled with config values, which
        is added into the config object
        """
        self.config = config or Configuration()
        self.config = extend_config(self.config, kwargs)

        self.extractor = ContentExtractor(self.config)

        # URL of the "best image" to represent this article
        self.top_img = self.top_image = ''

        # stores image provided by metadata
        self.meta_img = ''

        # All image urls in this article
        self.imgs = self.images = []

        # All videos in this article: youtube, vimeo, etc
        self.movies = []

        # Body text from this article
        self.text = ''

        # `keywords` are extracted via nlp() from the body text
        self.keywords = []

        # `meta_keywords` are extracted via parse() from <meta> tags
        self.meta_keywords = []

        # `tags` are also extracted via parse() from <meta> tags
        self.tags = set()

        # List of authors who have published the article, via parse()
        self.authors = []

        self.publish_date = ''

        # Summary generated from the article's body txt
        self.summary = ''

        # This article's unchanged and raw HTML
        self.html = ''

        # The HTML of this article's main node (most important part)
        self.article_html = ''

        # Keep state for downloads and parsing
        self.is_parsed = False
        self.download_state = ArticleDownloadState.NOT_STARTED
        self.download_exception_msg = None

        # Meta description field in the HTML source
        self.meta_description = ""

        # Meta language field in HTML source
        self.meta_lang = ""

        # Meta favicon field in HTML source
        self.meta_favicon = ""

        # Meta tags contain a lot of structured data, e.g. OpenGraph
        self.meta_data = {}

        # The canonical link of this article if found in the meta data
        self.canonical_link = ""

        # Holds the top element of the DOM that we determine is a candidate
        # for the main body of the article
        self.top_node = None

        # A deepcopied clone of the above object before heavy parsing
        # operations, useful for users to query data in the
        # "most important part of the page"
        self.clean_top_node = None

        # lxml DOM object generated from HTML
        self.doc = None

        # A deepcopied clone of the above object before undergoing heavy
        # cleaning operations, serves as an API if users need to query the DOM
        self.clean_doc = None

        # A property dict for users to store custom data.
        self.additional_data = {}

    def parse(self):
        self.doc = self.config.get_parser().fromstring(self.html)

        self.clean_doc = copy.deepcopy(self.doc)

        if self.doc is None:
            # `parse` call failed, return nothing
            return

        # # TODO: Fix this, sync in our fix_url() method
        # parse_candidate = self.get_parse_candidate()
        # self.link_hash = parse_candidate.link_hash  # MD5

        document_cleaner = DocumentCleaner(self.config)
        output_formatter = OutputFormatter(self.config)

        title = self.extractor.get_title(self.clean_doc)
        self.set_title(title)

        authors = self.extractor.get_authors(self.clean_doc)
        self.set_authors(authors)

        meta_lang = self.extractor.get_meta_lang(self.clean_doc)
        self.set_meta_language(meta_lang)

        if self.config.use_meta_language:
            self.extractor.update_language(self.meta_lang)
            output_formatter.update_language(self.meta_lang)

        meta_favicon = self.extractor.get_favicon(self.clean_doc)
        self.set_meta_favicon(meta_favicon)

        meta_description = \
            self.extractor.get_meta_description(self.clean_doc)
        self.set_meta_description(meta_description)

        # canonical_link = self.extractor.get_canonical_link(
        #     self.url, self.clean_doc)
        # self.set_canonical_link(canonical_link)

        tags = self.extractor.extract_tags(self.clean_doc)
        self.set_tags(tags)

        meta_keywords = self.extractor.get_meta_keywords(
            self.clean_doc)
        self.set_meta_keywords(meta_keywords)

        meta_data = self.extractor.get_meta_data(self.clean_doc)
        self.set_meta_data(meta_data)

        # self.publish_date = self.extractor.get_publishing_date(
        #     self.url,
        #     self.clean_doc)

        # Before any computations on the body, clean DOM object
        self.doc = document_cleaner.clean(self.doc)

        self.top_node = self.extractor.calculate_best_node(self.doc)
        if self.top_node is not None:
            video_extractor = VideoExtractor(self.config, self.top_node)
            self.set_movies(video_extractor.get_videos())

            self.top_node = self.extractor.post_cleanup(self.top_node)

            self.clean_top_node = copy.deepcopy(self.top_node)

            text, article_html = output_formatter.get_formatted(
                self.top_node)
            self.set_article_html(article_html)
            self.set_text(text)

        self.is_parsed = True

    def has_top_image(self):
        return self.top_img is not None and self.top_img != ''

    def nlp(self):
        """Keyword extraction wrapper
        """
        self.throw_if_not_parsed_verbose()

        nlp.load_stopwords(self.config.get_language())
        text_keyws = list(nlp.keywords(self.text).keys())
        title_keyws = list(nlp.keywords(self.title).keys())
        keyws = list(set(title_keyws + text_keyws))
        self.set_keywords(keyws)

        max_sents = self.config.MAX_SUMMARY_SENT

        summary_sents = nlp.summarize(title=self.title, text=self.text, max_sents=max_sents)
        summary = '\n'.join(summary_sents)
        self.set_summary(summary)

    def set_reddit_top_img(self):
        """Wrapper for setting images. Queries known image attributes
        first, then uses Reddit's image algorithm as a fallback.
        """
        try:
            s = images.Scraper(self)
            self.set_top_img(s.largest_image_url())
        except TypeError as e:
            if "Can't convert 'NoneType' object to str implicitly" in e.args[0]:
                log.debug('No pictures found. Top image not set, %s' % e)
            elif 'timed out' in e.args[0]:
                log.debug('Download of picture timed out. Top image not set, %s' % e)
            else:
                log.critical('TypeError other than None type error. '
                             'Cannot set top image using the Reddit '
                             'algorithm. Possible error with PIL., %s' % e)
        except Exception as e:
            log.critical('Other error with setting top image using the '
                         'Reddit algorithm. Possible error with PIL, %s' % e)

    def set_title(self, input_title):
        if input_title:
            self.title = input_title[:self.config.MAX_TITLE]

    def set_text(self, text):
        text = text[:self.config.MAX_TEXT]
        if text:
            self.text = text

    def set_html(self, html):
        """Encode HTML before setting it
        """
        if html:
            if isinstance(html, bytes):
                html = self.config.get_parser().get_unicode_html(html)
            self.html = html
            self.download_state = ArticleDownloadState.SUCCESS

    def set_article_html(self, article_html):
        """Sets the HTML of just the article's `top_node`
        """
        if article_html:
            self.article_html = article_html

    def set_meta_img(self, src_url):
        self.meta_img = src_url
        self.set_top_img_no_check(src_url)

    def set_top_img(self, src_url):
        if src_url is not None:
            s = images.Scraper(self)
            if s.satisfies_requirements(src_url):
                self.set_top_img_no_check(src_url)

    def set_top_img_no_check(self, src_url):
        """Provide 2 APIs for images. One at "top_img", "imgs"
        and one at "top_image", "images"
        """
        self.top_img = src_url
        self.top_image = src_url

    def set_imgs(self, imgs):
        """The motive for this method is the same as above, provide APIs
        for both `article.imgs` and `article.images`
        """
        self.images = imgs
        self.imgs = imgs

    def set_keywords(self, keywords):
        """Keys are stored in list format
        """
        if not isinstance(keywords, list):
            raise Exception("Keyword input must be list!")
        if keywords:
            self.keywords = keywords[:self.config.MAX_KEYWORDS]

    def set_authors(self, authors):
        """Authors are in ["firstName lastName", "firstName lastName"] format
        """
        if not isinstance(authors, list):
            raise Exception("authors input must be list!")
        if authors:
            self.authors = authors[:self.config.MAX_AUTHORS]

    def set_summary(self, summary):
        """Summary here refers to a paragraph of text from the
        title text and body text
        """
        self.summary = summary[:self.config.MAX_SUMMARY]

    def set_meta_language(self, meta_lang):
        """Save langauges in their ISO 2-character form
        """
        if meta_lang and len(meta_lang) >= 2 and \
           meta_lang in get_available_languages():
            self.meta_lang = meta_lang[:2]

    def set_meta_keywords(self, meta_keywords):
        """Store the keys in list form
        """
        self.meta_keywords = [k.strip() for k in meta_keywords.split(',')]

    def set_meta_favicon(self, meta_favicon):
        self.meta_favicon = meta_favicon

    def set_meta_description(self, meta_description):
        self.meta_description = meta_description

    def set_meta_data(self, meta_data):
        self.meta_data = meta_data

    def set_canonical_link(self, canonical_link):
        self.canonical_link = canonical_link

    def set_tags(self, tags):
        self.tags = tags

    def set_movies(self, movie_objects):
        """Trim video objects into just urls
        """
        movie_urls = [o.src for o in movie_objects if o and o.src]
        self.movies = movie_urls

    def throw_if_not_parsed_verbose(self):
        """Parse `is_parsed` status -> log readable status
        -> maybe throw ArticleException
        """
        if not self.is_parsed:
            print('You must `parse()` an article first!')
            raise ArticleException()


class Selenium:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--disable-extensions')
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')

        data=open(os.getcwd() + "/.env").read()
        selenium_path = data.split('\n')[0].split('=')[1]
        # selenium_path = os.getcwd()+"/chromedriver"
        self.__driver = webdriver.Chrome(selenium_path, chrome_options=options)
        self.__driver.set_page_load_timeout(10)
        pass

    def split_address(self, fullAddress):
        hostParts = fullAddress.replace("http://", "").replace("https://", "").split("/")[0]
        return hostParts

    def search_keyword_based_on_google(self, keyword):
        self.go_page('https://www.google.co.kr')
        self.__driver.find_element_by_id('lst-ib').send_keys(keyword)
        self.__driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[3]/center/input[1]').click()
        pass

    def get_google_links(self):
        googleLinks = []

        gs = self.__driver.find_elements_by_class_name('g')

        for g in gs:
            href = g.find_element_by_tag_name('a').get_attribute('href')
            # print(href)
            googleLinks.append(href)

        return googleLinks

    def go_page(self, url):
        self.__driver.get(url)
        pass

    def get_current_url(self):
        return self.__driver.current_url

    def get_page_source(self):
        return self.__driver.page_source

    def get_bs_obj(self, pageSource):
        return BeautifulSoup(pageSource)

    def quit(self):
        self.__driver.quit()
        pass

    # 외부링크 리스트 얻기
    def get_external_links(self, bsObj, excludeUrl, keyword):
        externalLinks = []
        pattern = re.compile("^(http|www)((?!" + excludeUrl + ").)*$")

        pageSource = self.__driver.page_source
        bsObj = BeautifulSoup(pageSource)

        # 현재 URL을 포함하지 않으면서 http나 www로 시작하는 링크를 모두 찾습니다.
        for link in bsObj.findAll('a', href=pattern):
            if link.attrs['href'] is not None:
                if link.attrs['href'] not in externalLinks:
                    externalLinks.append(link.attrs['href'])

        return externalLinks

    # 내부링크 리스트 얻기
    def get_internal_links(self, bsObj, includeUrl, fullUrl, keyword):
        internalLinks = []
        pattern = re.compile("^(/|.*"+includeUrl+")")

        pageSource = self.__driver.page_source
        bsObj = BeautifulSoup(pageSource)

        # /로 시작하거나 includeUrl이 들어있는 링크를 모두 찾습니다.
        for link in bsObj.findAll('a', href=pattern):
            if link.attrs['href'] is not None:
                if "http" in link.attrs['href']:
                    if link.attrs['href'] not in internalLinks:
                        internalLinks.append(link.attrs['href'])
                else:
                    if link.attrs['href'] not in internalLinks:
                        if "//" in link.attrs['href']:
                            internalLinks.append(fullUrl.split("/")[0]+link.attrs['href'])
                        else:
                            internalLinks.append(fullUrl.split("/")[0]+"//"+includeUrl+link.attrs['href'])

        return internalLinks

    # 키워드를 포함한 태그에 있는 문자열 추출
    def get_keyword_text_in_tag(self, bsObj, current_url, keyword):
        list = []

        pageSource = self.__driver.page_source
        bsObj = BeautifulSoup(pageSource)

        document = bsObj.get_text('\n')
        document = re.sub('\n+', '\n', document)
        document = re.sub(' +', ' ', document)

        for sentence in document.split('\n'):
            list.append(sentence)

        return list
