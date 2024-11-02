import yaml

from utils.app_types import BaseQuestion, BaseQuery, BaseConfigUnit



def load_config(yaml_file_path: str) -> BaseConfigUnit:
    with open(yaml_file_path, 'r') as file:
        param = yaml.safe_load(file)

    query_list = []
    for query_item in param["queries"]:
        query = BaseQuery(query_item["content"])
        query_list.append(query)

    question_list = []
    for question_item in param["questions"]:
        if "content" not in question_item:
            raise ValueError("Question content is required in the config file")
        if "answer type" not in question_item:
            question_item["answer type"] = "string"
        question = BaseQuestion(question_item["content"], 
                                question_item["answer type"])
        question_list.append(question)

    return BaseConfigUnit(
        name=param["name"],
        queries=query_list,
        questions=question_list
    )