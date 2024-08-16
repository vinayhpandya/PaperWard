import arxiv

from search.base_search import BaseSearch, BaseSearchResult

class ArxivPySearch(BaseSearch):

    def __init__(self) -> None:
        super().__init__()
        self.client = arxiv.Client()

    def search(self, query: str, max_results: int, **kwargs) -> list[BaseSearchResult]:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        results = self.client.results(search)
        return [BaseSearchResult(entry.entry_id, entry.title, entry.summary, entry.updated) for entry in results]