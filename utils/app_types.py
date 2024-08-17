from typing import List, Union, OrderedDict, Literal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseSearchResult:
    """
    Fetched paper from the search engines like arXiv
    """
    entry_id: str
    title: str
    summary: str
    updated_time: Union[str, datetime]

@dataclass
class BaseQuestion:
    """
    Question to be asked to the paper
    """
    question: str
    answer_type: Literal['string', 'int', 'bool']

    def __str__(self) -> str:
        return f"{self.question} ({self.answer_type})"
    
    def __hash__(self) -> int:
        return hash(self.question)
    
@dataclass
class BaseQuery:
    query: str
    max_results: int = 10

@dataclass
class BaseConfigUnit:
    name: str
    queries: List[BaseQuery]
    questions: List[BaseQuestion]
    read_full_text: bool = False

@dataclass
class BaseAnswer:
    """
    Answer to the question, made by LLMs.
    relation field should be a number between 0, 1, and 2, where:
        0: The paper is unrelated to the question.
        1: The paper may answer the question in its full text.
        2: The paper answers the question in its summary.
    """
    relation: int
    answer: str

    def __str__(self) -> str:
        return f"{self.answer} (relation: {self.relation})"
    
    def __dict__(self) -> dict:
        return {
            "relation": self.relation,
            "answer": self.answer
        }

@dataclass
class BaseAnalysis:
    """
    Analysis of a single paper with multiple questions and answers   
    """
    entry_id: str
    chs_title: str
    chs_summary: str
    qa: OrderedDict[BaseQuestion, BaseAnswer]
    score: int

    def __str__(self) -> str:
        return f"{self.chs_title}: {self.chs_summary}\n{"\n".join([f'{q}: {a}' for q, a in self.qa.items()])}"

    def __dict__(self) -> dict:
        return {
            "title": self.chs_title,
            "summary": self.chs_summary,
            "qa": {str(q): a.__dict__() for q, a in self.qa.items()},
            "score": self.score
        }
    
@dataclass
class DatabaseItem:
    """
    Information to be stored in the database.
    the score field is used to rank the results
    """
    document: BaseSearchResult
    analysis: BaseAnalysis
    read: bool = False
    star: bool = False

