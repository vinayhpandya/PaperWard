from search.arxiv_api import ArxivAPISearch
from search.arxiv_py import ArxivPySearch
from search.arxiv_web import ArxivWebSearch
from search.pymed_api import PyMedAPISearch
from search.semantic_scholar_search import SemanticScholarSearch
from utils.app_types import BaseQuery, BaseSearchResult, SearchSource
from typing import List
import asyncio


def get_fusion_search_results(
    queries: list[BaseQuery], sources: List[SearchSource]
) -> list[BaseSearchResult]:
    """
    Get search results from multiple sources.
    """
    if "arxiv" in sources:
        arxiv_api_search = ArxivAPISearch()
        arxiv_py_search = ArxivPySearch()
        arxiv_web_search = ArxivWebSearch()
    if "pubmed" in sources:
        pymed_api_search = PyMedAPISearch()
    if "semantic" in sources:
        semantic_search = SemanticScholarSearch()

    results = {}
    for query_item in queries:
        query, max_results = query_item["content"], query_item["max_results"]

        if "arxiv" in sources:
            results_web = arxiv_web_search.search(query)
            results_api = arxiv_api_search.search(query, max_results)
            results_py = arxiv_py_search.search(query, max_results)
            results.update({entry.entry_id: entry for entry in results_web})
            results.update({entry.entry_id: entry for entry in results_api})
            results.update({entry.entry_id: entry for entry in results_py})
        if "pubmed" in sources:
            results_pubmed = pymed_api_search.search(query, max_results=max_results)
            results.update({entry.entry_id: entry for entry in results_pubmed})
        if "semantic" in sources:
            # Use the synchronous wrapper method instead of async
            results_semantic = semantic_search.search(query, max_results=max_results)
            results.update({entry.entry_id: entry for entry in results_semantic})

    # convert the dict to a list
    return list(results.values())
