from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from utils.app_types import Base, Arxiv, DatabaseItem, BaseSearchResult, BaseAnalysis, BaseQuestion, BaseAnswer
from typing import List, Union, OrderedDict
import logging

engine = create_engine('sqlite:///arxiv.db')
Base.metadata.create_all(engine)


def add_arxiv(database_item: DatabaseItem):
    document = database_item.document
    analysis = database_item.analysis

    with Session(engine) as session:
        new_arxiv = Arxiv(
            arxiv_id=document.entry_id,
            title=document.title,
            summary=document.summary,
            update_time=document.updated_time,
            chs_title=analysis.chs_title,
            chs_summary=analysis.chs_summary,
            qa_dict=analysis.__dict__()['qa'],
            score=analysis.score
        )

        session.add(new_arxiv)
        session.commit()


def get_arxiv(arxiv_ids: List[str]) -> List[Union[DatabaseItem, None]]:
    """
    Get arxiv items from the database, if not found, return None
    """
    with Session(engine) as session:
        results = []
        local_item_count = session.query(Arxiv).filter(Arxiv.arxiv_id.in_(arxiv_ids)).count()
        logging.info(f"Found {local_item_count} out of {len(arxiv_ids)} items in the database")
        for arxiv_id in arxiv_ids:
            arxiv = session.query(Arxiv).filter(Arxiv.arxiv_id == arxiv_id).first()
            if arxiv:
                item = DatabaseItem(
                    document=BaseSearchResult(
                    entry_id=arxiv.arxiv_id,
                    title=arxiv.title,
                    summary=arxiv.summary,
                    updated_time=arxiv.update_time
                ), analysis=BaseAnalysis(
                    entry_id=arxiv.arxiv_id,
                    chs_title=arxiv.chs_title,
                    chs_summary=arxiv.chs_summary,
                    qa=OrderedDict({BaseQuestion(q, 'string'): BaseAnswer(a['relation'], a['answer']) for q, a in arxiv.qa_dict.items()}),
                    score=int(arxiv.score)
                ))
                results.append(item)
            else:
                results.append(None)
        return results
