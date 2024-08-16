from search.base_search import BaseSearch, BaseSearchResult

import urllib, urllib.request
import xml.etree.ElementTree as ET

class ArxivAPISearch(BaseSearch):

    def search(self, query: str, max_results: int, **kwargs) -> list[BaseSearchResult]:
        # replace spaces with + in the query
        query = query.replace(' ', '+')

        url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}'
        data = urllib.request.urlopen(url)
        tree = ET.parse(data)
        root = tree.getroot()

        results = []

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
            updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
            paper_url = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']

            # remove \n and \t from the title and summary
            title = title.replace('\n', '').replace('\t', '')
            summary = summary.replace('\n', '').replace('\t', '')

            results.append(BaseSearchResult(paper_url, title, summary, updated))

        return results