from search.fusion_search import get_fusion_search_results
from analysis.base_process import batch_analysis
from analysis.rank_results import rank_results
from configs.read_yaml import load_config
from utils.app_types import DatabaseItem
from visualization.write_html import write_html
from storage.database import add_arxiv, get_arxiv
import asyncio


def main(yaml_path: str = "configs/example_config.yaml",
         html_path: str = "output.html",
         rpm_limit: int = 10):
    # TODO: enable multiple configs
    config = load_config(yaml_path)
    logging.info(f"config loaded from {yaml_path}")
    
    # search related papers
    search_results = get_fusion_search_results(config.queries)
    logging.info(f"search results fetched")

    # compare the search results with the database to avoid duplicate analysis
    local_database_items = get_arxiv([search_result.entry_id for search_result in search_results])
    # only keeps the search results that are not in the database
    search_results = [search_result for i, search_result in enumerate(search_results) if local_database_items[i] is None]

    # use LLMs to answer the questions in the search results
    # avoid breaking the rpm limit of the API
    analyse_results = []
    for i in range(0, len(search_results), rpm_limit):
        logging.info(f"Analysing search item {i} to {i+rpm_limit}")
        analyse_batch = asyncio.run(batch_analysis(search_results[i:i+rpm_limit], config.questions))
        analyse_results.extend(analyse_batch)

    # weave the analysis results with the search results
    new_database_items = [DatabaseItem(search_result, analysis) for search_result, analysis in zip(search_results, analyse_results)]

    # add the new items to the database
    for i in new_database_items:
        add_arxiv(i)

    # rank the analysis results
    all_database_items = new_database_items + [i for i in local_database_items if i is not None]
    ranked_results = rank_results(all_database_items)
    
    # write the results to an HTML file
    write_html(ranked_results, html_path)

    # open the html file in the default web browser
    import webbrowser
    webbrowser.open(html_path)

    

if __name__ == '__main__':
    import logging
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)
    logging.debug(f"Logging initialized at level {logging_level}")
    
    # parse system arguments
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--configs', type=str, default="configs/example_config.yaml",
                        help='path to the yaml config file')
    parser.add_argument('--output', type=str, default="output.html",
                        help='path to the output html file')
    parser.add_argument('--rpm', type=int, default=10,
                        help='the rpm limit of the API')
    args = parser.parse_args()

    main(args.configs, args.output, args.rpm)
