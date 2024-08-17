from search.fusion_search import get_fusion_search_results
from analysis.base_process import batch_analysis
from utils.app_types import BaseQuestion
import asyncio


def main():
    # TODO: load yaml files to initialize the questions and query
    # TODO: enable multiple queries and questions
    query = 'LLM games'
    questions = [BaseQuestion("How the paper uses LLMs to design the policy in computer games?", 'string'),
                 BaseQuestion("How the paper uses LLMs to create computer games?", 'string')]
    
    # search related papers
    search_results = get_fusion_search_results(query)

    # TODO: compare the search results with the database to avoid duplicate analysis

    # use LLMs to answer the questions in the search results
    # avoid breaking the rpm limit of the API
    rpm_limit = 10
    analyse_results = []
    for i in range(0, len(search_results), rpm_limit):
        analyse_batch = asyncio.run(batch_analysis(search_results[i:i+rpm_limit], questions))
        analyse_results.extend(analyse_batch)
    
    # TODO: store the analysis results in the database
    for analysis in analyse_results:
        print(analysis.__dict__())

    

if __name__ == '__main__':
    import logging
    logging_level = logging.WARN
    logging.basicConfig(level=logging_level)
    logging.debug(f"Logging initialized at level {logging_level}")
    main()
