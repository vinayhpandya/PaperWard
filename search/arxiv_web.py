from search.base_search import BaseSearch, BaseSearchResult
from search.arxiv_py import ArxivPySearch

import requests
from lxml import html
import arxiv

class ArxivWebSearch(BaseSearch):
    arxiv_py_search: ArxivPySearch

    def __init__(self) -> None:
        super().__init__()
        self.arxiv_py_client = arxiv.Client()


    def search(self, query: str, start:int = 0, **kwargs) -> list[BaseSearchResult]:
        # replace spaces with + in the query
        query = query.replace(' ', '+')

        url = f'https://arxiv.org/search/?query={query}&searchtype=all&source=header&start={start}'
        tree = self.fetch_and_parse_html(url)
        list_items = tree.xpath('//p[@class="list-title is-inline-block"]/a')
        urls = [entry.attrib['href'].split('/abs/')[1] for entry in list_items]

        search_by_id = arxiv.Search(id_list=urls)
        items = self.arxiv_py_client.results(search_by_id)
        results = [BaseSearchResult(entry.entry_id, entry.title, entry.summary, entry.updated) for entry in items]
        return results
    
    @staticmethod
    def fetch_and_parse_html(url):
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content
                tree = html.fromstring(response.text)
                return tree
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return []