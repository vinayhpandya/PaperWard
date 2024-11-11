# PaperWard

![logo](docs/logo.png "logo")

Say goodbye to endless scrolling through research papers! With PaperWard, you can set a watch on key sites like ArXiv to stay up-to-date effortlessly on the latest developments in your field. 

PaperWard is your personal research assistant, automatically fetching papers, analyzing them based on your custom questions, and delivering concise summaries with relevant findings.


## Key Features

### Automated Paper Fetching with Relevance Ranking

No more manual browsing! PaperWard continuously retrieves the latest papers that match your interests from supported websites* using your custom queries. 

It also prioritizes papers based on their relevance to your defined criteria, allowing you to focus only on the most pertinent research.

![Automated Paper Fetching](docs/Screenshot_1.png "Automated Paper Fetching")


### Customizable, User-Driven Analysis

Skip the irrelevant details! Define the questions you care about, and PaperWard will read each paper and answer these questions for you.

![User-Driven Analysis](docs/Screenshot_2.png "User-Driven Analysis")

### Built-In Translation

Break the language barrier! PaperWard translates paper information into your preferred language**, while displaying original text at the same time.

![Translation](docs/Screenshot_3.png "Translation")

---

*Currently supports ArXiv abstracts only.  
**Supports simplified Chinese translation at this time.

## Installation and Requirements
This project runs well on Python 3.12 on Windows. We have not tested it on other platforms.
```
pip install arxiv requests lxml openai retrying PyYAML SQLAlchemy pymed streamlit
```

You need to get an OpenAI API key to use PaperWard. You can sign up for an API key at https://platform.openai.com/signup. Once you have the key, you can set it as an environment variable `OPENAI_API_KEY`.

```bash
export OPENAI_API_KEY=<your_openai_api_key>
```

PaperWard uses `gpt-4o` as the default LLM model. You can change it by modifying the source code in `utils/llm_handler.py`.



## Usage

(1) Create a config file following the template below. The `queries` field should contain a list of search keywords that you want to track. The `questions` field should contain a list of questions that you want to ask about the papers. `configs/example_config.yaml` is an example of a config file.

```yaml
name: LLM academic agents

queries:
- content: LLM academic research agent
  max_results: 10
- content: LLM academic writing
  max_results: 10

questions:
- content: "How does the paper use LLMs to optimize academic research?"
- content: "What fields of research does the paper focus on?"
- content: "What stages of academic research does the paper focus on?"
```

(2) Run the script with the following command:

```bash
python app.py --config <path_to_config_file> --output <path_to_output_html> [--rpm <requests_per_minute>]
```

example:

```bash
python app.py --config configs/example_config.yaml --output output.html
```

(3) The script will download the latest papers from the web and analyse them using the predefined questions. The answers will be stored in a database named `papers.db`. Then a webpage will be generated with the papers and their answers. All papers are ranked by the relevance of the questions to the papers.


## Call for Contributions!

Apparently, the project is still at its early stages and has a lot of room for improvement. We welcome contributions from the community to make PaperWard more powerful and user-friendly. Here are some of the areas where you can contribute:

- **Support for more websites**: Currently, PaperWard only supports ArXiv. We would like to add support for more websites like PubMed, IEEE Xplore, etc.

- **Support for more languages**: Currently, PaperWard only supports simplified Chinese. We would like to add support for more languages.

- **Support for dynamic question update**: Currently, if you change the questions in the config file, previously-fetched papers will not be re-analyzed. We would like to add support for dynamic question updates.

- **Support for more question types**: Currently, PaperWard only supports simple questions. We would like to add support for more complex questions like multiple-choice questions, etc.

- **More user-friendly interface**: Currently, PaperWard only generates a static HTML file as the report. We would like to add support for more interactive interfaces.
