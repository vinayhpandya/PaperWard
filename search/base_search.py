from utils.app_types import BaseSearchResult

class BaseSearch:
    def search(self, query: str, max_results: int, **kwargs) -> list[BaseSearchResult]:
        raise NotImplementedError