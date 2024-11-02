from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from utils.app_types import Base, Arxiv  # Adjust this import based on where your Arixv class is defined

def load_all_arxiv_data():
    # Create engine
    engine = create_engine('sqlite:///arxiv.db')

    # Create a session
    with Session(engine) as session:
        # Create a select statement
        stmt = select(Arxiv)

        # Execute the query
        results = session.execute(stmt).scalars().all()

        # Print the results
        if results:
            print(f"Found {len(results)} records in the arxiv table:")
            for record in results:
                print(f"\nID: {record.arxiv_id}")
                print(f"Title: {record.title}")
                print(f"Summary: {record.summary[:100]}...")  # Print first 100 characters of summary
                print(f"Update Time: {record.update_time}")
                print(f"Chinese Title: {record.chs_title}")
                print(f"Chinese Summary: {record.chs_summary[:100]}...")  # Print first 100 characters of Chinese summary
                print("-" * 50)
        else:
            print("No records found in the arxiv table.")

if __name__ == "__main__":
    load_all_arxiv_data()