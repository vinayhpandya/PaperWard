# PaperWard

![logo](docs/logo.png "logo")

提高你的论文浏览效率！使用 PaperWard，您可以在 ArXiv 等网站上设定你的关注议题(插眼)，轻松跟踪您领域的最新进展。

PaperWard 是您的私人研究助手，会根据您自定义的问题自动获取、分析论文，并提供简明的相关研究报告。

## 主要功能

### 自动搜索排序！
PaperWard 将根据您的自定义查询，从支持的网站*中持续获取符合您兴趣的最新论文，并根据您定义的问题与论文的相关性来优先排序，帮助您专注于最相关的研究。

![Automated Paper Fetching](docs/Screenshot_1.png "Automated Paper Fetching")

### 定制分析！

您可以定义自己关心的问题，PaperWard 将根据您设定的问题来分析论文。

![User-Driven Analysis](docs/Screenshot_2.png "User-Driven Analysis")

### 打破语言障碍！

PaperWard 会将论文信息翻译为您的首选语言**，让研究变得触手可及。

![Translation](docs/Screenshot_3.png "Translation")

---

*目前仅支持 ArXiv 摘要。  
**目前仅支持简体中文翻译。

## 安装要求

该项目在 Windows 上的 Python 3.12 版本上运行良好。尚未在其他平台上进行测试。

```bash
pip install arxiv requests lxml openai retrying PyYAML SQLAlchemy
```

您需要获得 OpenAI 的 API 密钥来使用 PaperWard。您可以在 https://platform.openai.com/signup 注册获取 API 密钥。得到密钥后，您可以将其设置为环境变量 `OPENAI_API_KEY`。

```bash
export OPENAI_API_KEY=<您的密钥>
```

## 使用方法

1. 根据以下模板创建一个配置文件。`queries` 字段应包含您要跟踪的搜索关键词列表。`questions` 字段应包含您想要询问论文的问题列表。`configs/example_config.yaml` 是一个配置文件示例。

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

2. 使用以下命令运行脚本：

```bash
python app.py --config <path_to_config_file> --output <path_to_output_html> [--rpm <requests_per_minute>]
```

示例：

```bash
python app.py --config configs/example_config.yaml --output output.html
```

3. 脚本将从网上下载最新的论文并回答问题，答案将被存储在名为 `papers.db` 的数据库中。随后将生成一个包含论文及其答案的网页。所有论文将按问题与论文的相关性进行排序。

## 欢迎贡献！

显然，该项目仍处于早期阶段，尚有很大的改进空间。我们欢迎社区的贡献，让 PaperWard 更强大、更友好。以下是您可以贡献的一些方面：

- **支持更多网站**：目前仅支持 ArXiv。我们希望增加对 PubMed、IEEE Xplore 等更多网站的支持。
- **支持更多语言**：目前仅支持简体中文。我们希望增加更多语言支持。
- **支持动态问题更新**：目前，如果您更改配置文件中的问题，已获取的论文不会重新分析。我们希望增加对动态问题更新的支持。
- **支持更多问题类型**：目前仅支持简单问题。我们希望增加对更复杂问题的支持，如多项选择题等。
- **更友好的用户界面**：目前仅生成一个静态 HTML 文件作为报告。我们希望增加更多互动界面的支持。