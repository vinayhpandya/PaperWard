import streamlit as st
from search.fusion_search import get_fusion_search_results
from analysis.base_process import batch_analysis
from analysis.rank_results import rank_results
from configs.read_yaml import load_config
from utils.app_types import PaperItem
from storage.database import add_arxiv, get_arxiv
from visualization.write_html import write_html, compose_html
import asyncio
import logging
import yaml

# Streamlit Configuration
st.set_page_config(page_title="Research Paper Search App", layout="wide")

# Streamlit UI Components
st.title("Research Paper Search Application")

# User input for search
query = st.text_input("Enter your search query:")

# Source selection
st.subheader("Select Search Sources")
col1, col2 = st.columns(2)
with col1:
    use_arxiv = st.checkbox("arXiv", value=True)
with col2:
    use_pubmed = st.checkbox("PubMed", value=False)

# Validate at least one source is selected
if not (use_arxiv or use_pubmed):
    st.warning("Please select at least one search source.")

# Rate limit selection
rpm_limit = st.slider(
    "Rate Limit (Requests per Minute)", min_value=1, max_value=50, value=10
)

# Placeholder for the search results
results_placeholder = st.empty()


# Function to handle the main logic of the search
def main(query, rpm_limit, sources):
    # Define the configuration dynamically
    config = {
        "name": "LLM RAG",
        "sources": sources,
        "queries": [{"content": query, "max_results": 5}],
        "questions": [
            {"content": "What retrieval methods are used in this paper?"},
            {"content": "Does the retrieval method involve traditional IR techniques?"},
            {"content": "What scenarios are the retrieval methods used in?"},
        ],
    }
    logging.info(f"Config created with query: {query}")

    # Search related papers
    search_results = get_fusion_search_results(config["queries"], config["sources"])
    logging.info(f"Search results fetched")

    # Compare the search results with the database to avoid duplicate analysis
    local_database_items = get_arxiv(
        [search_result.entry_id for search_result in search_results]
    )
    search_results = [
        search_result
        for i, search_result in enumerate(search_results)
        if local_database_items[i] is None
    ]

    # Use LLMs to answer the questions in the search results, failed results will be None
    analyse_results = []
    for i in range(0, len(search_results), rpm_limit):
        logging.info(f"Analysing search item {i} to {i + rpm_limit}")
        analyse_batch = asyncio.run(
            batch_analysis(search_results[i : i + rpm_limit], config["questions"])
        )
        analyse_results.extend(analyse_batch)

    # Create new database items, excluding the ones that failed analysis
    new_database_items = [
        PaperItem(search_result, analysis)
        for search_result, analysis in zip(search_results, analyse_results) if analysis
    ]

    # Add the new items to the database
    for item in new_database_items:
        add_arxiv(item)

    # Rank the analysis results
    all_database_items = new_database_items + [
        item for item in local_database_items if item is not None
    ]
    ranked_results = rank_results(all_database_items)

    return ranked_results


# Trigger search on button click
if st.button("Search") and query:
    if not (use_arxiv or use_pubmed):
        st.error("Please select at least one search source before searching.")
    else:
        # Create list of selected sources
        selected_sources = []
        if use_arxiv:
            selected_sources.append("arxiv")
        if use_pubmed:
            selected_sources.append("pubmed")

        with st.spinner("Fetching and analyzing search results..."):
            print(f"Fetching and analyzing search results from sources: {selected_sources}")
            # Get the ranked results
            ranked_results = main(query, rpm_limit, selected_sources)

            # Display results using the existing HTML template
            for result in ranked_results:
                document = result.document
                analysis = result.analysis
                with st.container():
                    st.markdown(f"### {analysis.chs_title} {document.title}")
                    st.write(f"**Score:** {analysis.score} pts")
                    st.write(f"**Updated Time:** {document.updated_time}")
                    st.write(f"**Read Status:** {result.read}")
                    st.write(f"**Summary:** {document.summary}")
                    st.write(f"**Translated Summary:** {analysis.chs_summary}")
                    st.write("**Q&A:**")
                    for question, answer in analysis.qa.items():
                        if isinstance(question, str):
                            question_str = question
                        else:
                            question_str = question.question
                        st.write(
                            f"- **{question_str}**: {answer.answer} (Relation: {answer.relation})"
                        )
                    st.markdown("---")

# Footer
st.markdown("---")
st.write("Powered by Streamlit")
