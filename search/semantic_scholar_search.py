from search.base_search import BaseSearch, BaseSearchResult
from typing import List
import httpx
import logging
import asyncio
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

logger = logging.getLogger("semanticscholar")


class SemanticScholarSearch(BaseSearch):
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.timeout = timeout
        self.headers = {"Accept": "application/json"}

    def search(
        self, query: str, max_results: int = 5, **kwargs
    ) -> List[BaseSearchResult]:
        """
        Synchronous search method that wraps the async implementation.
        """
        # Create a new event loop if there isn't one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.search_async(query, max_results, **kwargs))

    async def search_async(
        self, query: str, max_results: int = 5, **kwargs
    ) -> List[BaseSearchResult]:
        """
        Async search implementation.
        """
        try:
            params = {
                "query": query,
                "limit": max_results,
                "fields": "paperId,title,abstract,publicationDate",
            }

            async with httpx.AsyncClient() as client:
                response = await self._make_request(
                    client=client, endpoint="/paper/search", parameters=params
                )

            if not response or "data" not in response:
                return []

            results = response["data"][:max_results]

            return [
                BaseSearchResult(
                    entry_id=paper.get("paperId", ""),
                    title=paper.get("title", "No title available"),
                    summary=paper.get("abstract", "No abstract available"),
                    updated_time=paper.get("publicationDate"),
                )
                for paper in results
            ]

        except Exception as e:
            logger.error(f"Error in semantic scholar search: {str(e)}")
            return []

    @retry(
        wait=wait_fixed(30),
        retry=retry_if_exception_type(ConnectionRefusedError),
        stop=stop_after_attempt(3),
    )
    async def _make_request(
        self, client: httpx.AsyncClient, endpoint: str, parameters: dict
    ) -> dict:
        url = f"{self.base_url}{endpoint}"

        response = await client.get(
            url, params=parameters, headers=self.headers, timeout=self.timeout
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise ConnectionRefusedError("Rate limit exceeded")
        elif response.status_code == 404:
            logger.warning(f"No results found for query")
            return {}
        else:
            logger.error(f"API request failed with status {response.status_code}")
            response.raise_for_status()
