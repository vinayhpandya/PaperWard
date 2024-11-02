# PaperWard

Placing a ward on ArXiv to keep track of the latest papers in your field.

## Installation
This project runs well on Python 3.12 on Windows. We have not tested it on other platforms.
```
pip install arxiv requests lxml openai retrying PyYAML SQLAlchemy
```

## Usage

(1) Create a config file following the template below. The `queries` field should contain a list of search keywords that you want to track. The `questions` field should contain a list of questions that you want to ask about the papers. `configs/example_config.yaml` is an example of a config file.

```yaml
name: LLM academic agents

queries:
- content: LLM academic agent
- content: LLM academic writing
- content: LLM writing agent

questions:
- content: "How does the paper use LLMs to optimize academic writing?"
- content: "What are the limitations of the paper's approach?"
```

(2) Run the script with the following command:

```bash
python app.py --config <path_to_config_file> --output <path_to_output_html> [--rpm <requests_per_minute>]
```

example:

```bash
python app.py --config configs/example_config.yaml --output output.html
```

(3) The script will download the latest papers from arXiv and ask questions about them. The answers will be stored in a database named `papers.db`. Then a webpage will be generated with the papers and their answers. All papers are ranked by the relevance of the questions to the papers.