from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from utils.app_types import Base, Arixv, DatabaseItem

engine = create_engine('sqlite:///arxiv.db')
Base.metadata.create_all(engine)


def add_arxiv(database_item: DatabaseItem):
    document = database_item.document
    analysis = database_item.analysis

    with Session(engine) as session:
        new_arxiv = Arixv(
            arxiv_id=document.entry_id,
            title=document.title,
            summary=document.summary,
            update_time=document.updated_time,
            chs_title=analysis.chs_title,
            chs_summary=analysis.chs_summary,
        )

        session.add(new_arxiv)
        session.commit()
