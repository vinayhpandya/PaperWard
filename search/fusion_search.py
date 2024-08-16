from search.arxiv_api import ArxivAPISearch
from search.arxiv_py import ArxivPySearch
from search.arxiv_web import ArxivWebSearch
from search.base_search import BaseSearchResult


def get_fusion_search_results(query: str) -> list[BaseSearchResult]:
    arxiv_api_search = ArxivAPISearch()
    arxiv_py_search = ArxivPySearch()
    arxiv_web_search = ArxivWebSearch()

    results_web = arxiv_web_search.search(query)
    results_api = arxiv_api_search.search(query, 15)
    results_py = arxiv_py_search.search(query, 15)

    # get the union of the results, using the entry_id as the key
    results = {entry.entry_id: entry for entry in results_web}
    results.update({entry.entry_id: entry for entry in results_api})
    results.update({entry.entry_id: entry for entry in results_py})

    # convert the dict to a list
    return list(results.values())

