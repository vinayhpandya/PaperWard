from typing import List, OrderedDict
from retrying import retry
import json
import asyncio
import re
import logging

from utils.llm_handler import LLMHandler
from utils.app_types import BaseSearchResult, BaseQuestion, BaseAnswer, BaseAnalysis


PROMPT = """
You are good academic researcher. You have been tasked with analyzing a paper summary and filling out a questionnaire.

# Paper

Title: {title}
Summary: {summary}

# Questionnaire
Please fill out the following questionnaire and return *only* the JSON object. Do not include any additional text or comments.

```json
{
    "chs_title": "<please translate the title to Chinese>",
    "chs_summary": "<please translate the summary to Chinese>",
    "questions": {questions}
}
```

# Note

- You should fill out the questionnaire above and return as a JSON object.
- The `relation` field should be a number between 0, 1, and 2, where:
    - 0: The paper is unrelated to the question.
    - 1: The paper may answer the question in its full text.
    - 2: The paper answers the question in its summary.
"""


def question_format(questions: List[BaseQuestion]) -> str:
    question_list = []
    for question in questions:
        question_list.append(
            {
                "question": question["content"],
                "relation": "<return 0, 1, or 2>",
                "answer": "<fill your answer here. the format needs to be in string>",
            }
        )
    return json.dumps(question_list)


@retry(stop_max_attempt_number=5)
def single_analysis(
    result: BaseSearchResult, questions: List[BaseQuestion]
) -> BaseAnalysis:
    # logging.info(f"Analyzing {result.title}")
    question_str = question_format(questions)
    prompt = (
        PROMPT.replace("{questions}", question_str)
        .replace("{title}", result.title)
        .replace("{summary}", result.summary)
    )
    llm_handler = LLMHandler()
    response = llm_handler.chat_with_gpt(prompt)
    json_text = re.findall(r"```json(.*)```", response, re.DOTALL)[-1]
    try:
        # use utf-8 to avoid decoding errors
        response = json.loads(json_text.encode("utf-8"))
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {json_text} \n {e}")
        raise ValueError(f"Failed to decode JSON: {json_text}")

    question_dict = OrderedDict()
    total_score = 0
    for idx, item in enumerate(response["questions"]):
        answer = BaseAnswer(int(item["relation"]), item["answer"])
        question = item["question"]
        question_dict[question] = answer
        total_score += answer.relation

    # logging.info(f"Analysis of {result.title} completed")
    return BaseAnalysis(
        result.entry_id,
        response["chs_title"],
        response["chs_summary"],
        question_dict,
        total_score,
    )


async def single_analysis_wrapper(
    result: BaseSearchResult, questions: List[BaseQuestion]
) -> BaseAnalysis:
    return await asyncio.to_thread(single_analysis, result, questions)


async def batch_analysis(
    results: List[BaseSearchResult], questions: List[BaseQuestion]
) -> List[BaseAnalysis]:
    tasks = [single_analysis_wrapper(result, questions) for result in results]
    analysis_results = await asyncio.gather(*tasks)
    return analysis_results
