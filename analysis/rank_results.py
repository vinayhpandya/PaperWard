from typing import List, Tuple

from utils.app_types import PaperItem


def rank_results(results: List[PaperItem]) -> List[PaperItem]:
    return sorted(results, key=lambda x: x.analysis.score, reverse=True)
