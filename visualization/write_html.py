from typing import List, OrderedDict

from utils.app_types import DatabaseItem, BaseSearchResult, BaseAnalysis, BaseQuestion, BaseAnswer

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paper Feed</title>
    <link rel="stylesheet" href="./visualization/style.css">
</head>

<body>
    <main>
    {content}
    </main>
</body>
</html>
"""

def write_html(database_items: List[DatabaseItem], html_path: str) -> None:
    html_content = compose_html(database_items)
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

def compose_html(database_items: List[DatabaseItem]) -> str:
    html_content = ""
    for db_item in database_items:
        document: BaseSearchResult = db_item.document
        analysis: BaseAnalysis = db_item.analysis
        html_part = f"""
        <section>
            <span class="totalScore">{analysis.score} pts</span>
            <h1>{analysis.chs_title} {document.title}</h1>
            <div class="info">
                <span class="read">{db_item.read}</span>
                <span class="time">{document.updated_time}</span>
                <a href="{document.entry_id}">web page</a>
            </div>
            <div class="content">
                <p>{analysis.chs_summary}</p>
                <p>{document.summary}</p>
            </div>
            <div class="qa">
                {qa_html(analysis.qa)}
            </div>
        </section>
        """
        html_content += html_part

    return HTML_TEMPLATE.format(content=html_content)
        

def qa_html(qa: OrderedDict[BaseQuestion, BaseAnswer]) -> str:
    qa_content = ""
    for question, answer in qa.items():
        qa_part = f"""
        <div class="qa-item score{answer.relation}">
            <h2 class="question">{question.question}</h2>
            <p class="answer"><span class="relation">{answer.relation} pts</span>{answer.answer}</p>
        </div>
        """
        qa_content += qa_part
    return qa_content