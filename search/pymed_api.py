from search.base_search import BaseSearch, BaseSearchResult
from pymed import PubMed


class PyMedAPISearch(BaseSearch):

    def __init__(self) -> None:
        super().__init__()
        self.pubmed = PubMed(tool="MyTool", email="vinayharshadpandya27@gmail.com")

    def search(self, query: str, max_results: int, **kwargs) -> list[BaseSearchResult]:
        results = self.pubmed.query(query=query, max_results=max_results)
        return [
            BaseSearchResult(
                entry.pubmed_id, entry.title, entry.abstract, entry.publication_date
            )
            for entry in results
        ]
