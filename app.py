from search.fusion_search import get_fusion_search_results
from analysis.base_process import batch_analysis
from configs.read_yaml import load_config
import asyncio


def main(yaml_path: str = "configs/example_config.yaml",
         rpm_limit: int = 10):
    # TODO: enable multiple configs
    config = load_config(yaml_path)
    
    # search related papers
    search_results = get_fusion_search_results(config.queries)
    logging.info(f"search results fetched")

    # TODO: compare the search results with the database to avoid duplicate analysis

    # use LLMs to answer the questions in the search results
    # avoid breaking the rpm limit of the API
    
    analyse_results = []
    for i in range(0, len(search_results), rpm_limit):
        logging.info(f"Analysing search item {i} to {i+rpm_limit}")
        analyse_batch = asyncio.run(batch_analysis(search_results[i:i+rpm_limit], config.questions))
        analyse_results.extend(analyse_batch)
    
    # TODO: store the analysis results in the database
    for analysis in analyse_results:
        print(analysis.__dict__())

    

if __name__ == '__main__':
    import logging
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)
    logging.debug(f"Logging initialized at level {logging_level}")
    main()
