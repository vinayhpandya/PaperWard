from typing import List, Tuple

from utils.app_types import DatabaseItem


def rank_results(results: List[DatabaseItem]) -> List[DatabaseItem]:
    return sorted(results, key=lambda x: x.analysis.score, reverse=True)
