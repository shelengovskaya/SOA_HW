import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


class Grabber:

    def __init__(self, url):
        self.url= url
        self.total_urls_visited = 0
        self.internal_urls = set()
        self.external_urls = set()
        self.urls = set()

        self.get_all_website_links()


    @staticmethod
    def is_valid(link):
        parsed = urlparse(link)
        return bool(parsed.netloc) and bool(parsed.scheme)


    def get_all_website_links(self):

        domain_name = urlparse(self.url).netloc

        try:
            soup = BeautifulSoup(requests.get(self.url).content, "html.parser")
        except:
            return []

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href is None:
                continue

            href = urljoin(self.url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path


            if not self.is_valid(href):
                continue

            if domain_name not in href:
                self.external_urls.add(href)
            else:
                # print(domain_name, href)
                self.internal_urls.add(href)

            self.urls.add(href)


    def get_all_urls(self):
        return self.urls

    def get_internal_urls(self):
        return self.internal_urls

    def get_external_urls(self):
        return self.external_urls
