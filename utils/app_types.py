from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy import String, JSON
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
class PaperItem:
    """
    Contains paper information and its analysis.
    Used for front-end filtering+visualization and bridge to the database.
    the score field is used to rank the results
    """
    document: BaseSearchResult
    analysis: BaseAnalysis
    read: bool = False
    star: bool = False


class Base(DeclarativeBase):
    pass


class PaperDBItem(MappedAsDataclass, Base):
    """Used to store the paper information in the database"""
    __tablename__ = 'arxiv'

    arxiv_id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(String(10_000))
    update_time: Mapped[str] = mapped_column(String(50))
    chs_title: Mapped[str] = mapped_column(String(500))
    chs_summary: Mapped[str] = mapped_column(String(10_000))

    qa_dict: Mapped[dict] = mapped_column(JSON)
    score: Mapped[int] = mapped_column(String(50))

    def __repr__(self):
        return f"<Arxiv(id={self.arxiv_id}, title='{self.title}', summary='{self.summary}, update_time='{self.update_time}, chs_title='{self.chs_title}, chs_summary='{self.chs_summary},')>"

